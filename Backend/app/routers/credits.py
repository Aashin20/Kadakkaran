import sqlite3

from fastapi import APIRouter, HTTPException, status

from app.database import get_db, utc_now
from app.schemas import CreditCreate, CreditUpdate


router = APIRouter(prefix="/credits", tags=["Credits"])


def credit_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "amount": row["amount"],
        "created_at": row["created_at"],
        "pay_at": row["pay_at"],
        "paid_at": row["paid_at"],
        "is_paid": row["paid_at"] is not None,
    }


def get_credit_or_404(db: sqlite3.Connection, credit_id: int) -> sqlite3.Row:
    row = db.execute("SELECT * FROM credits WHERE id = ?", (credit_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit not found")
    return row


@router.post("", status_code=status.HTTP_201_CREATED)
def add_credit(payload: CreditCreate):
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO credits (name, amount, created_at, pay_at, paid_at)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (
                payload.name.strip(),
                payload.amount,
                utc_now(),
                payload.pay_at.isoformat(),
            ),
        )
        return credit_dict(get_credit_or_404(db, cursor.lastrowid))


@router.get("")
def list_credits():
    with get_db() as db:
        rows = db.execute("SELECT * FROM credits ORDER BY created_at DESC, id DESC").fetchall()
        return [credit_dict(row) for row in rows]


@router.get("/{credit_id}")
def view_credit(credit_id: int):
    with get_db() as db:
        return credit_dict(get_credit_or_404(db, credit_id))


@router.patch("/{credit_id}")
def update_credit(credit_id: int, payload: CreditUpdate):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided")
    if "name" in updates:
        updates["name"] = updates["name"].strip()
    if "pay_at" in updates:
        updates["pay_at"] = updates["pay_at"].isoformat()

    set_clause = ", ".join(f"{column} = ?" for column in updates)
    values = list(updates.values()) + [credit_id]
    with get_db() as db:
        get_credit_or_404(db, credit_id)
        db.execute(f"UPDATE credits SET {set_clause} WHERE id = ?", values)
        return credit_dict(get_credit_or_404(db, credit_id))


@router.post("/{credit_id}/pay")
def mark_credit_paid(credit_id: int):
    paid_at = utc_now()
    with get_db() as db:
        get_credit_or_404(db, credit_id)
        db.execute(
            "UPDATE credits SET paid_at = ? WHERE id = ?",
            (paid_at, credit_id),
        )
        return credit_dict(get_credit_or_404(db, credit_id))


@router.delete("/{credit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credit(credit_id: int):
    with get_db() as db:
        get_credit_or_404(db, credit_id)
        db.execute("DELETE FROM credits WHERE id = ?", (credit_id,))
        return None
