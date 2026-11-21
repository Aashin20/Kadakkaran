from fastapi import APIRouter, HTTPException, status

from app.database import get_db, utc_now
from app.routers.products import get_product_or_404
from app.schemas import StockChange


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
            (product_id, payload.quantity, payload.note, now),
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
            (product_id, payload.quantity, payload.note, now),
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
