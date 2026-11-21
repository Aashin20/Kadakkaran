from fastapi import APIRouter, HTTPException, status
import base64

from app.database import get_db, utc_now
from app.routers.bill import generate_bill_pdf
from app.routers.products import get_product_or_404
from app.schemas import BillCreate, StockChange


router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("/sales/summary")
def sales_summary():
    with get_db() as db:
        total = db.execute(
            "SELECT COALESCE(SUM(total), 0) AS total, COALESCE(SUM(profit), 0) AS profit "
            "FROM sales "
            "WHERE substr(created_at, 1, 10) = strftime('%Y-%m-%d', 'now')"
        ).fetchone()
        sold = db.execute(
            "SELECT COALESCE(SUM(quantity), 0) AS quantity FROM sales "
            "WHERE substr(created_at, 1, 10) = strftime('%Y-%m-%d', 'now')"
        ).fetchone()
        return {
            "total_sales": total["total"],
            "profit": total["profit"],
            "quantity_sold": sold["quantity"],
        }


@router.get("/sales/top")
def top_selling_products(limit: int = 5):
    limit = min(max(limit, 1), 10)
    with get_db() as db:
        rows = db.execute(
            """
            SELECT p.id, p.name,
                   COALESCE(SUM(s.quantity), 0) AS sold_quantity,
                   COALESCE(SUM(s.total), 0) AS revenue
            FROM products p
            LEFT JOIN sales s ON s.product_id = p.id
            GROUP BY p.id, p.name
            HAVING COALESCE(SUM(s.quantity), 0) > 0
            ORDER BY sold_quantity DESC, revenue DESC, p.name
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


@router.get("")
def view_all_stock():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, sku, stock, price FROM products ORDER BY id"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "sku": row["sku"],
                "stock": row["stock"],
                "price": row["price"],
            }
            for row in rows
        ]


@router.post("/checkout")
def checkout_bill(payload: BillCreate):
    merged: dict[int, int] = {}
    for item in payload.items:
        merged[item.product_id] = merged.get(item.product_id, 0) + item.quantity

    now = utc_now()
    checked_items: list[dict] = []
    with get_db() as db:
        for product_id, quantity in merged.items():
            product = get_product_or_404(db, product_id)
            if quantity > product["stock"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product['name']}. Available: {product['stock']}",
                )
            checked_items.append({
                "product_id": product["id"],
                "name": product["name"],
                "quantity": quantity,
                "price": product["price"],
                "cost": product["cost"],
                "stock": product["stock"],
            })

        subtotal = sum(item["price"] * item["quantity"] for item in checked_items)
        discount = min(payload.discount, subtotal)
        total = subtotal - discount
        profit = sum(
            (item["price"] - item["cost"]) * item["quantity"]
            for item in checked_items
        ) - discount
        profit = round(profit, 2)

        last_sale_id = db.execute("SELECT COALESCE(MAX(id), 100) AS id FROM sales").fetchone()["id"]
        bill_id = last_sale_id + 1

        for item in checked_items:
            new_stock = item["stock"] - item["quantity"]
            db.execute(
                "UPDATE products SET stock = ?, sold = sold + ?, updated_at = ? WHERE id = ?",
                (new_stock, item["quantity"], now, item["product_id"]),
            )
            db.execute(
                """
                INSERT INTO stock_movements
                    (product_id, quantity, movement_type, note, created_at)
                VALUES (?, ?, 'OUT', ?, ?)
                """,
                (item["product_id"], item["quantity"], "Sold", now),
            )
            item_total = item["price"] * item["quantity"]
            item_profit = (item["price"] - item["cost"]) * item["quantity"]
            db.execute(
                """
                INSERT INTO sales
                    (product_id, quantity, price, cost, total, profit, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["product_id"],
                    item["quantity"],
                    item["price"],
                    item["cost"],
                    item_total,
                    item_profit,
                    now,
                ),
            )

    response = {
        "bill_id": bill_id,
        "items": checked_items,
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "total": round(total, 2),
        "profit": profit,
        "pdf_base64": None,
    }
    if payload.generate_pdf:
        pdf_bytes = generate_bill_pdf(bill_id, checked_items, discount, total)
        response["pdf_base64"] = base64.b64encode(pdf_bytes).decode("ascii")
    return response


@router.get("/{product_id}")
def view_product_stock(product_id: int):
    with get_db() as db:
        product = get_product_or_404(db, product_id)
        return {"id": product["id"], "sku": product["sku"], "stock": product["stock"]}


@router.post("/{product_id}/add")
def add_stock(product_id: int, payload: StockChange):
    now = utc_now()
    with get_db() as db:
        product = get_product_or_404(db, product_id)
        new_stock = product["stock"] + payload.quantity
        db.execute(
            "UPDATE products SET stock = ?, updated_at = ? WHERE id = ?",
            (new_stock, now, product_id),
        )
        db.execute(
            """
            INSERT INTO stock_movements
                (product_id, quantity, movement_type, note, created_at)
            VALUES (?, ?, 'IN', ?, ?)
            """,
            (product_id, payload.quantity, payload.note or "Stock added", now),
        )
        return {"id": product_id, "stock": new_stock, "quantity_added": payload.quantity}


@router.post("/{product_id}/remove")
def remove_stock(product_id: int, payload: StockChange):
    now = utc_now()
    with get_db() as db:
        product = get_product_or_404(db, product_id)
        if payload.quantity > product["stock"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product['stock']}",
            )
        new_stock = product["stock"] - payload.quantity
        is_sale = bool(payload.note and (
            "sale" in payload.note.lower() or "വിൽപ്പന" in payload.note
        ))
        db.execute(
            "UPDATE products SET stock = ?, sold = sold + ?, updated_at = ? WHERE id = ?",
            (new_stock, payload.quantity if is_sale else 0, now, product_id),
        )
        db.execute(
            """
            INSERT INTO stock_movements
                (product_id, quantity, movement_type, note, created_at)
            VALUES (?, ?, 'OUT', ?, ?)
            """,
            (product_id, payload.quantity, "Sold" if is_sale else payload.note, now),
        )
        if is_sale:
            total = product["price"] * payload.quantity
            profit = (product["price"] - product["cost"]) * payload.quantity
            db.execute(
                """
                INSERT INTO sales
                    (product_id, quantity, price, cost, total, profit, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    payload.quantity,
                    product["price"],
                    product["cost"],
                    total,
                    profit,
                    now,
                ),
            )
        return {"id": product_id, "stock": new_stock, "quantity_removed": payload.quantity}


@router.get("/{product_id}/movements")
def view_stock_movements(product_id: int):
    with get_db() as db:
        get_product_or_404(db, product_id)
        rows = db.execute(
            """
            SELECT id, quantity, movement_type, note, created_at
            FROM stock_movements
            WHERE product_id = ?
            ORDER BY id DESC
            """,
            (product_id,),
        ).fetchall()
        return [dict(row) for row in rows]
