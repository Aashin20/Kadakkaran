import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "erp.db"


@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def initialize_database() -> None:
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                description TEXT,
                price REAL NOT NULL CHECK (price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                movement_type TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT')),
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                created_at TEXT NOT NULL,
                pay_at TEXT NOT NULL,
                paid_at TEXT
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                price REAL NOT NULL CHECK (price >= 0),
                cost REAL NOT NULL CHECK (cost >= 0),
                total REAL NOT NULL CHECK (total >= 0),
                profit REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );
            """
        )

        product_columns = {
            row["name"]: row["name"]
            for row in db.execute("PRAGMA table_info(products)").fetchall()
        }
        migrations = {
            "cost": "ALTER TABLE products ADD COLUMN cost REAL NOT NULL DEFAULT 0",
            "unit": "ALTER TABLE products ADD COLUMN unit TEXT NOT NULL DEFAULT 'കിലോ'",
            "minimum_stock": "ALTER TABLE products ADD COLUMN minimum_stock INTEGER NOT NULL DEFAULT 5",
            "sold": "ALTER TABLE products ADD COLUMN sold INTEGER NOT NULL DEFAULT 0",
            "expiry_days": "ALTER TABLE products ADD COLUMN expiry_days INTEGER",
        }
        for column, statement in migrations.items():
            if column not in product_columns:
                db.execute(statement)

        product_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if product_count == 0:
            now = utc_now()
            seed_products = [
                ("മട്ട അരി", "RICE-001", "പ്രിമിയം മട്ട അരി", 52, 44, 38, "കിലോ", 20, 60, None),
                ("പഞ്ചസാര", "SUGAR-001", "കറുത്ത പഞ്ചസാര", 46, 41, 6, "കിലോ", 15, 48, None),
                ("വെളിച്ചെണ്ണ", "OIL-001", "വിഴിക്കുന്ന വെളിച്ചെണ്ണ", 220, 198, 12, "ലിറ്റർ", 10, 35, None),
                ("ചായപ്പൊടി", "TEA-001", "ബ്ലെൻഡ് ചായപ്പൊടി", 120, 104, 0, "പാക്കറ്റ്", 8, 30, None),
                ("തുവരപ്പരിപ്പ്", "DAL-001", "ശുദ്ധമായ തുവരപ്പരിപ്പ്", 150, 132, 14, "കിലോ", 10, 22, None),
                ("ഉപ്പ്", "SALT-001", "ഐഡഡ് സോഡിയം ഉപ്പ്", 20, 16, 30, "പാക്കറ്റ്", 10, 40, None),
                ("മുളകുപൊടി", "CHILI-001", "ചുവന്ന മുളകുപൊടി", 90, 74, 4, "പാക്കറ്റ്", 6, 18, None),
                ("ബിസ്കറ്റ്", "BISC-001", "മരിച്ചെങ്കിലും മുറം ബിസ്കറ്റ്", 10, 8, 70, "എണ്ണം", 30, 90, None),
                ("പാൽ", "MILK-001", "പാൽ പാക്കറ്റ്", 28, 25, 20, "പാക്കറ്റ്", 15, 120, 2),
                ("സോപ്പ്", "SOAP-001", "കൈ സോപ്പ്", 38, 30, 25, "എണ്ണം", 8, 5, None),
            ]
            db.executemany(
                """
                INSERT INTO products (
                    name, sku, description, price, cost, stock, unit,
                    minimum_stock, sold, expiry_days, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        name, sku, description, price, cost, stock, unit,
                        minimum_stock, sold, expiry_days, now, now,
                    )
                    for name, sku, description, price, cost, stock, unit,
                    minimum_stock, sold, expiry_days in seed_products
                ],
            )

        stock_movement_count = db.execute(
            "SELECT COUNT(*) FROM stock_movements"
        ).fetchone()[0]
        product_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if stock_movement_count < product_count:
            now = utc_now()
            products = db.execute(
                """
                SELECT p.id, p.stock
                FROM products p
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM stock_movements sm
                    WHERE sm.product_id = p.id
                )
                ORDER BY p.id
                """
            ).fetchall()
            seed_movements = []
            for product in products:
                seed_movements.append(
                    (
                        product["id"],
                        max(1, product["stock"]),
                        "IN",
                        "Opening stock",
                        now,
                    )
                )
            db.executemany(
                """
                INSERT INTO stock_movements
                    (product_id, quantity, movement_type, note, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                seed_movements,
            )

        credit_count = db.execute("SELECT COUNT(*) FROM credits").fetchone()[0]
        if credit_count == 0:
            now = utc_now()
            seed_credits = [
                ("രമേശ്", 800, "2026-11-24T18:00:00Z", None),
                ("ലക്ഷ്മി ചേച്ചി", 1250, "2026-11-26T18:00:00Z", None),
                ("അബ്ദുള്ള", 400, "2026-11-23T18:00:00Z", now),
                ("സുരേഷ്", 750, "2026-11-28T18:00:00Z", None),
                ("അനിത", 300, "2026-11-25T18:00:00Z", None),
            ]
            db.executemany(
                """
                INSERT INTO credits (name, amount, created_at, pay_at, paid_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (name, amount, now, pay_at, paid_at)
                    for name, amount, pay_at, paid_at in seed_credits
                ],
            )
