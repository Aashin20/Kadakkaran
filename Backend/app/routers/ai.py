import json
import os
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any
from pathlib import Path

from fastapi import APIRouter, HTTPException
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.database import get_db, utc_now
from app.schemas import AIChatRequest


router = APIRouter(prefix="/ai", tags=["AI"])


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def find_product(db, name: str = "", product_id: int | None = None):
    if product_id is not None:
        row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    else:
        rows = db.execute("SELECT * FROM products").fetchall()
        clean = re.sub(r"\s+", "", name).lower()
        row = None
        for candidate in rows:
            candidate_clean = re.sub(r"\s+", "", candidate["name"]).lower()
            if clean and (
                candidate_clean in clean
                or clean in candidate_clean
                or SequenceMatcher(None, candidate_clean, clean).ratio() >= 0.72
            ):
                row = candidate
                break
    return row


def list_products() -> dict[str, Any]:
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, sku, description, price, stock FROM products ORDER BY id"
        ).fetchall()
    return {"products": [dict(row) for row in rows]}


def list_stock(args: dict[str, Any]) -> dict[str, Any]:
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, sku, stock, price FROM products ORDER BY id"
        ).fetchall()
    stock = [dict(row) for row in rows]
    if args.get("low_only"):
        stock = [item for item in stock if item["stock"] <= 10]
    return {"stock": stock}


def analytics() -> dict[str, Any]:
    with get_db() as db:
        products = db.execute(
            "SELECT id, name, stock, price FROM products"
        ).fetchall()
        credits = db.execute(
            "SELECT name, amount, paid_at FROM credits"
        ).fetchall()
        movements = db.execute(
            """
            SELECT movement_type, SUM(quantity) AS quantity
            FROM stock_movements
            GROUP BY movement_type
            """
        ).fetchall()
        low_stock = db.execute(
            "SELECT id, name, stock FROM products WHERE stock <= 10 ORDER BY stock, name"
        ).fetchall()
        top_selling = db.execute(
            """
            SELECT p.id, p.name,
                   COALESCE(SUM(s.quantity), 0) AS sold_quantity,
                   COALESCE(SUM(s.total), 0) AS revenue
            FROM products p
            LEFT JOIN sales s ON s.product_id = p.id
            GROUP BY p.id, p.name
            HAVING COALESCE(SUM(s.quantity), 0) > 0
            ORDER BY sold_quantity DESC, revenue DESC, p.name
            LIMIT 5
            """
        ).fetchall()

    product_list = [dict(row) for row in products]
    credit_list = [dict(row) for row in credits]
    return {
        "inventory_value": sum(row["stock"] * row["price"] for row in product_list),
        "total_stock": sum(row["stock"] for row in product_list),
        "low_stock": [dict(row) for row in low_stock],
        "stock_movements": [dict(row) for row in movements],
        "outstanding_credit": sum(
            row["amount"] for row in credit_list if row["paid_at"] is None
        ),
        "top_stock": sorted(product_list, key=lambda row: row["stock"], reverse=True)[:5],
        "top_selling": [dict(row) for row in top_selling],
    }


def top_selling(args: dict[str, Any]) -> dict[str, Any]:
    try:
        limit = int(args.get("limit", 5))
    except (TypeError, ValueError):
        limit = 5
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
    return {
        "top_selling": [dict(row) for row in rows],
        "count": len(rows),
    }


def list_credits(args: dict[str, Any]) -> dict[str, Any]:
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, amount, created_at, pay_at, paid_at FROM credits "
            "ORDER BY created_at DESC"
        ).fetchall()
    credits = [dict(row) for row in rows]
    if args.get("unpaid_only"):
        credits = [item for item in credits if item["paid_at"] is None]
    return {"credits": credits}


def find_credit(db, credit_id: Any = None, name: str = "", unpaid_only: bool = False):
    if credit_id is not None:
        try:
            row = db.execute(
                "SELECT * FROM credits WHERE id = ?", (int(credit_id),)
            ).fetchone()
            if row is not None:
                if unpaid_only and row["paid_at"] is not None:
                    return None
                return row
        except (TypeError, ValueError):
            pass

    clean = re.sub(r"\s+", "", name).strip().lower()
    if not clean:
        return None

    name_aliases = {
        "രമേശ്": {"ramesh", "rameesh", "rames", "ramesh"},
        "ലക്ഷ്മിചേച്ചി": {"lakshmi", "lakshmichechi", "lakshmi chechi"},
        "അബ്ദുള്ള": {"abdulla", "abdullah", "abdulla"},
        "സുരേഷ്": {"suresh", "sures"},
        "അനിത": {"anitha", "anita"},
    }

    sql = "SELECT * FROM credits"
    if unpaid_only:
        sql += " WHERE paid_at IS NULL"
    sql += " ORDER BY id DESC"
    rows = db.execute(sql).fetchall()

    for row in rows:
        candidate = re.sub(r"\s+", "", row["name"]).strip().lower()
        if candidate == clean:
            return row
        aliases = next(
            (
                aliases
                for malayalam_name, aliases in name_aliases.items()
                if re.sub(r"\s+", "", malayalam_name).lower() == candidate
            ),
            set(),
        )
        if clean in {re.sub(r"\s+", "", alias).lower() for alias in aliases}:
            return row

    for row in rows:
        candidate = re.sub(r"\s+", "", row["name"]).strip().lower()
        if clean in candidate or candidate in clean:
            return row

    best_row = None
    best_score = 0.0
    for row in rows:
        candidate = re.sub(r"\s+", "", row["name"]).strip().lower()
        score = SequenceMatcher(None, candidate, clean).ratio()
        if score > best_score:
            best_row = row
            best_score = score
    return best_row if best_score >= 0.72 else None


def to_number(value: Any) -> float | None:
    """Accept 10, 10.0 and "10" (the model is not consistent about types)."""
    if isinstance(value, bool):
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def adjust_stock(args: dict[str, Any]) -> dict[str, Any]:
    product_id = args.get("product_id")
    product_name = args.get("product_name", "")
    number = to_number(args.get("quantity"))
    quantity = int(number) if number is not None and number == int(number) else None
    operation = args.get("operation")
    if quantity is None or quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be a positive integer")
    if operation not in ("add", "remove"):
        raise HTTPException(status_code=400, detail="operation must be add or remove")

    with get_db() as db:
        product = find_product(db, product_name, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if operation == "remove" and quantity > product["stock"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {product['stock']}",
            )
        new_stock = (
            product["stock"] + quantity
            if operation == "add"
            else product["stock"] - quantity
        )
        now = utc_now()
        is_sale = operation == "remove"
        db.execute(
            "UPDATE products SET stock = ?, sold = sold + ?, updated_at = ? WHERE id = ?",
            (new_stock, quantity if is_sale else 0, now, product["id"]),
        )
        db.execute(
            """
            INSERT INTO stock_movements
                (product_id, quantity, movement_type, note, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                product["id"],
                quantity,
                "IN" if operation == "add" else "OUT",
                "Sold" if is_sale else "Groq AI stock adjustment",
                now,
            ),
        )
        if is_sale:
            total = product["price"] * quantity
            profit = (product["price"] - product["cost"]) * quantity
            db.execute(
                """
                INSERT INTO sales
                    (product_id, quantity, price, cost, total, profit, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["id"],
                    quantity,
                    product["price"],
                    product["cost"],
                    total,
                    profit,
                    now,
                ),
            )
    return {
        "product_id": product["id"],
        "product": product["name"],
        "operation": operation,
        "quantity": quantity,
        "stock": new_stock,
    }


def prepare_bill(args: dict[str, Any]) -> dict[str, Any]:
    raw_items = args.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise HTTPException(status_code=400, detail="Bill items are required")

    items: list[dict[str, Any]] = []
    with get_db() as db:
        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                continue
            number = to_number(raw_item.get("quantity"))
            quantity = int(number) if number is not None and number == int(number) else None
            if quantity is None or quantity <= 0:
                raise HTTPException(status_code=400, detail="quantity must be a positive integer")

            product = find_product(
                db,
                str(raw_item.get("product_name", "")),
                raw_item.get("product_id"),
            )
            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product not found: {raw_item.get('product_name', '')}",
                )
            if quantity > product["stock"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product['name']}. Available: {product['stock']}",
                )

            items.append({
                "product_id": product["id"],
                "name": product["name"],
                "quantity": quantity,
                "price": product["price"],
                "stock": product["stock"],
                "total": product["price"] * quantity,
            })

    return {
        "items": items,
        "cart_total": sum(item["total"] for item in items),
        "count": sum(item["quantity"] for item in items),
    }


def add_credit(args: dict[str, Any]) -> dict[str, Any]:
    name = str(args.get("name", "")).strip()
    amount = to_number(args.get("amount"))
    pay_at = args.get("pay_at")
    if not name or amount is None or amount <= 0:
        raise HTTPException(status_code=400, detail="name and positive amount are required")
    try:
        pay_at_value = datetime.fromisoformat(pay_at) if pay_at else datetime.now(timezone.utc)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="pay_at must be an ISO datetime")

    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO credits (name, amount, created_at, pay_at, paid_at)
            VALUES (?, ?, ?, ?, NULL)
            """,
            (name, float(amount), utc_now(), pay_at_value.isoformat()),
        )
        row = db.execute("SELECT * FROM credits WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return {"credit": dict(row)}


def mark_credit_paid(args: dict[str, Any]) -> dict[str, Any]:
    credit_id = args.get("credit_id")
    name = str(args.get("name", "")).strip()
    with get_db() as db:
        row = find_credit(db, credit_id, name, unpaid_only=True)
        if row is None:
            raise HTTPException(status_code=404, detail="Credit record not found")
        db.execute(
            "UPDATE credits SET paid_at = ? WHERE id = ?",
            (utc_now(), row["id"]),
        )
        updated = db.execute("SELECT * FROM credits WHERE id = ?", (row["id"],)).fetchone()
    return {"credit": dict(updated)}


def update_credit(args: dict[str, Any]) -> dict[str, Any]:
    credit_id = args.get("credit_id")
    name = str(args.get("name", "")).strip()
    updates: dict[str, Any] = {}

    if "amount" in args:
        amount = to_number(args.get("amount"))
        if amount is None or amount <= 0:
            raise HTTPException(status_code=400, detail="amount must be a positive number")
        updates["amount"] = float(amount)
    elif "amount_change" in args:
        amount_change = to_number(args.get("amount_change"))
        if amount_change is None:
            raise HTTPException(status_code=400, detail="amount_change must be a number")
        updates["_amount_change"] = float(amount_change)

    if "new_name" in args:
        new_name = str(args.get("new_name", "")).strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="new_name cannot be empty")
        updates["name"] = new_name
    elif "name_update" in args:
        new_name = str(args.get("name_update", "")).strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="name_update cannot be empty")
        updates["name"] = new_name

    if "pay_at" in args:
        try:
            pay_at = datetime.fromisoformat(str(args["pay_at"]))
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="pay_at must be an ISO datetime")
        updates["pay_at"] = pay_at.isoformat()

    if not updates:
        raise HTTPException(status_code=400, detail="No credit fields provided to update")

    with get_db() as db:
        row = find_credit(db, credit_id, name)
        if row is None:
            raise HTTPException(status_code=404, detail="Credit record not found")

        amount_change = updates.pop("_amount_change", None)
        if amount_change is not None:
            next_amount = float(row["amount"]) + amount_change
            if next_amount <= 0:
                raise HTTPException(status_code=400, detail="Updated credit amount must be positive")
            updates["amount"] = next_amount

        set_clause = ", ".join(f"{column} = ?" for column in updates)
        db.execute(
            f"UPDATE credits SET {set_clause} WHERE id = ?",
            [*updates.values(), row["id"]],
        )
        updated = db.execute("SELECT * FROM credits WHERE id = ?", (row["id"],)).fetchone()
    return {"credit": dict(updated)}


TOOLS = {
    "list_products": lambda args: list_products(),
    "list_stock": list_stock,
    "low_stock": lambda args: list_stock({"low_only": True}),
    "analytics": lambda args: analytics(),
    "top_selling": top_selling,
    "list_credits": list_credits,
    "adjust_stock": adjust_stock,
    "prepare_bill": prepare_bill,
    "add_credit": add_credit,
    "update_credit": update_credit,
    "mark_credit_paid": mark_credit_paid,
}


def parse_tool_arguments(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"tool": "general", "args": {}, "reason": content}
    if not isinstance(parsed, dict):
        return {"tool": "general", "args": {}}
    return parsed


@router.post("/chat")
def chat(payload: AIChatRequest):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured on the backend",
        )

    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    tool_names = ", ".join(TOOLS.keys())
    routing = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=300,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "നിങ്ങൾ Kadakaran ERP Malayalam assistant ആണ്. "
                    "User request-നെ താഴെയുള്ള one JSON object ആയി output ചെയ്യുക. "
                    f"Available tools: {tool_names}, general. "
                    "JSON keys: tool, args. "
                    "Use adjust_stock args: operation(add/remove), product_name, quantity. "
                    "If a request is a bill/sale, use prepare_bill with args {items:[{product_name,quantity},...]}. "
                    "Never execute prepare_bill: it only prepares the checkout preview. "
                    "Use add_credit args: name, amount, optional pay_at. "
                    "Use update_credit args: name or credit_id, plus amount, amount_change, "
                    "new_name/name_update, or pay_at. "
                    "Use mark_credit_paid args: name or credit_id. "
                    "Use list_credits args: unpaid_only. "
                    "Use top_selling args: optional limit for questions about the most/best-selling "
                    "or top-selling products. "
                    "Use analytics for inventory, sales summary, profit, and stock analytics questions. "
                    "Never invent a name or ID. For stock questions use list_stock/low_stock/analytics."
                ),
            },
            {"role": "user", "content": payload.message},
        ],
    )
    routing_output = routing.choices[0].message.content or ""
    decision = parse_tool_arguments(routing_output)
    print(f"Groq routing output: {routing_output}", flush=True)

    tool_name = decision.get("tool", "general")
    args = decision.get("args", {})
    if not isinstance(args, dict):
        args = {}

    if tool_name in TOOLS:
        # A failed action is not an HTTP error here: it goes into the result so
        # the spoken/written reply can tell the user what went wrong.
        try:
            tool_result = TOOLS[tool_name](args)
        except HTTPException as exc:
            tool_result = {"error": str(exc.detail)}
        except Exception as exc:
            tool_result = {"error": f"Could not execute {tool_name}: {exc}"}
        print(f"Tool {tool_name}({args}) -> {tool_result}", flush=True)
    else:
        tool_result = {
            "answer_hint": "User asked a general question or clarification.",
            "available_tools": list(TOOLS.keys()),
        }

    answer = client.chat.completions.create(
        model=model,
        temperature=0.3,
        max_tokens=600,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Kadakaran AI. Reply only in natural Malayalam. "
                    "Your reply is read aloud, so use short plain sentences: "
                    "no markdown, no bullet lists, no emojis. "
                    "Be concise and useful. Use the provided structured result. "
                    "If the result contains an error, explain the problem briefly. "
                    "For actions, confirm what changed. For analytics, include the actual numbers. "
                    "Never include decimal points or decimal fractions in the spoken reply. "
                    "Round every amount or quantity to the nearest whole number. "
                    "Do not claim an action happened unless it is in the result."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original Malayalam request: {payload.message}\n"
                    f"Executed tool: {tool_name}\n"
                    f"Structured result: {json.dumps(tool_result, ensure_ascii=False)}"
                ),
            },
        ],
    )
    groq_reply = answer.choices[0].message.content or ""
    groq_reply = remove_decimal_numbers(groq_reply)
    print(f"Groq response: {groq_reply}", flush=True)

    endpoint = None
    method = None
    if "error" in tool_result:
        pass
    elif tool_name == "adjust_stock":
        operation = args.get("operation")
        product_id = tool_result.get("product_id")
        if operation in ("add", "remove") and product_id is not None:
            method = "POST"
            endpoint = f"/stock/{product_id}/{operation}"
    elif tool_name == "add_credit":
        credit = tool_result.get("credit")
        method = "POST"
        endpoint = "/credits"
        if isinstance(credit, dict) and credit.get("id") is not None:
            endpoint = f"/credits/{credit['id']}"
    elif tool_name == "update_credit":
        credit = tool_result.get("credit")
        credit_id = credit.get("id") if isinstance(credit, dict) else None
        if credit_id is not None:
            method = "PATCH"
            endpoint = f"/credits/{credit_id}"
    elif tool_name == "mark_credit_paid":
        credit = tool_result.get("credit")
        credit_id = credit.get("id") if isinstance(credit, dict) else None
        if credit_id is not None:
            method = "PATCH"
            endpoint = f"/credits/{credit_id}/pay"
    elif tool_name == "list_products":
        method = "GET"
        endpoint = "/products"
    elif tool_name in ("list_stock", "low_stock"):
        method = "GET"
        endpoint = "/stock"
    elif tool_name == "list_credits":
        method = "GET"
        endpoint = "/credits"
    elif tool_name == "analytics":
        method = "GET"
        endpoint = "/stock"
    elif tool_name == "top_selling":
        method = "GET"
        endpoint = "/stock/sales/top"

    return {
        "reply": groq_reply,
        "tool": tool_name,
        "function": tool_name,
        "ok": "error" not in tool_result,
        "method": method,
        "endpoint": endpoint,
        "result": tool_result,
    }


# ---- text to speech (Sarvam) -------------------------------------------------

TTS_CHUNK_CHARS = 800  # Sarvam allows 2500 (bulbul:v3); shorter chunks come back faster


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def remove_decimal_numbers(text: str) -> str:
    """Round decimal numbers to whole numbers before text is shown or spoken."""
    decimal_pattern = re.compile(r"(?<![\w])[-+]?\d[\d,]*\.\d+(?![\w])")

    def round_number(match: re.Match[str]) -> str:
        value = match.group(0).replace(",", "")
        try:
            rounded = Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            return str(int(rounded))
        except (InvalidOperation, ValueError):
            return match.group(0)

    return decimal_pattern.sub(round_number, text)


def clean_for_speech(text: str) -> str:
    text = remove_decimal_numbers(text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[*_#`>|~]+", " ", text)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", " ", text)
    # Sarvam recommends commas in numbers above 4 digits so they are read as one number.
    text = re.sub(r"(?<![\d,.])(\d{5,})(?![\d,.])", lambda m: f"{int(m.group(1)):,}", text)
    return re.sub(r"\s+", " ", text).strip()


def split_for_speech(text: str, limit: int = TTS_CHUNK_CHARS) -> list[str]:
    chunks: list[str] = []
    current = ""
    for sentence in re.split(r"(?<=[.!?\u0964])\s+", text):
        while len(sentence) > limit:
            cut = sentence.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if current:
                chunks.append(current)
                current = ""
            chunks.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if current and len(current) + len(sentence) + 1 > limit:
            chunks.append(current)
            current = ""
        current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return [chunk for chunk in chunks if chunk]


@router.post("/tts")
def text_to_speech(payload: TTSRequest):
    api_key = os.getenv("SARVAM_API_KEY") or os.getenv("SARVAM_API_SUBSCRIPTION_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="SARVAM_API_KEY is not configured on the backend")

    text = clean_for_speech(payload.text)
    if not text:
        raise HTTPException(status_code=400, detail="Nothing to speak")

    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=api_key)
    audios: list[str] = []
    try:
        for chunk in split_for_speech(text):
            response = client.text_to_speech.convert(
                text=chunk,
                language_code="ml-IN",
                model=os.getenv("SARVAM_TTS_MODEL", "bulbul:v3"),
                speaker=os.getenv("SARVAM_TTS_SPEAKER", "shubh"),
                output_audio_codec="wav",
            )
            audios.extend(response.audios or [])
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Text to speech failed: {exc}") from exc

    # Each entry is a complete base64-encoded WAV; the browser plays them in order.
    return {"audios": audios, "format": "wav"}
