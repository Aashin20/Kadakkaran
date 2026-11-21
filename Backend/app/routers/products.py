import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.database import get_db, utc_now
from app.schemas import ProductCreate, ProductUpdate


router = APIRouter(prefix="/products", tags=["Products"])


def product_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "sku": row["sku"],
        "description": row["description"],
        "price": row["price"],
        "cost": row["cost"],
        "stock": row["stock"],
        "unit": row["unit"],
        "minimum_stock": row["minimum_stock"],
        "sold": row["sold"],
        "expiry_days": row["expiry_days"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_product_or_404(db: sqlite3.Connection, product_id: int) -> sqlite3.Row:
    row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return row


@router.post("", status_code=status.HTTP_201_CREATED)
def add_product(payload: ProductCreate):
    now = utc_now()
    with get_db() as db:
        try:
            cursor = db.execute(
                """
                INSERT INTO products (
                    name, sku, description, price, cost, stock, unit,
                    minimum_stock, expiry_days, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.name.strip(),
                    payload.sku.strip(),
                    payload.description,
                    payload.price,
                    payload.cost,
                    payload.initial_stock,
                    payload.unit.strip() or "കിലോ",
                    payload.minimum_stock,
                    payload.expiry_days,
                    now,
                    now,
                ),
            )
            product_id = cursor.lastrowid
            if payload.initial_stock > 0:
                db.execute(
                    """
                    INSERT INTO stock_movements
                        (product_id, quantity, movement_type, note, created_at)
                    VALUES (?, ?, 'IN', 'Initial stock', ?)
                    """,
                    (product_id, payload.initial_stock, now),
                )
            return product_dict(get_product_or_404(db, product_id))
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this SKU already exists",
            )


@router.get("")
def list_products(search: Optional[str] = Query(default=None, max_length=200)):
    with get_db() as db:
        if search:
            pattern = f"%{search}%"
            rows = db.execute(
                """
                SELECT * FROM products
                WHERE name LIKE ? OR sku LIKE ? OR description LIKE ?
                ORDER BY id
                """,
                (pattern, pattern, pattern),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM products ORDER BY id").fetchall()
        return [product_dict(row) for row in rows]


@router.get("/{product_id}")
def view_product(product_id: int):
    with get_db() as db:
        return product_dict(get_product_or_404(db, product_id))


@router.patch("/{product_id}")
def update_product(product_id: int, payload: ProductUpdate):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided")

    if "name" in updates:
        updates["name"] = updates["name"].strip()
    if "sku" in updates:
        updates["sku"] = updates["sku"].strip()
    updates["updated_at"] = utc_now()

    set_clause = ", ".join(f"{column} = ?" for column in updates)
    values = list(updates.values()) + [product_id]
    with get_db() as db:
        get_product_or_404(db, product_id)
        try:
            db.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this SKU already exists",
            )
        return product_dict(get_product_or_404(db, product_id))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    with get_db() as db:
        get_product_or_404(db, product_id)
        db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return None
