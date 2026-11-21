from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

FONT_DIR = Path(__file__).parent / "fonts"

BRAND = (0, 102, 204)
DARK = (33, 37, 41)
MUTED = (108, 117, 125)
ZEBRA = (244, 248, 253)
LINE = (222, 226, 230)


class BillPDF(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=22)

        latin_regular = FONT_DIR / "NotoSans-Regular.ttf"
        latin_bold = FONT_DIR / "NotoSans-Bold.ttf"
        mal_regular = FONT_DIR / "NotoSansMalayalam-Regular.ttf"
        mal_bold = FONT_DIR / "NotoSansMalayalam-Bold.ttf"

        if not latin_regular.exists():
            latin_regular = Path(r"C:\Windows\Fonts\arial.ttf")
        if not latin_bold.exists():
            latin_bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
        if not mal_regular.exists():
            mal_regular = latin_regular
        if not mal_bold.exists():
            mal_bold = latin_bold

        if latin_regular.exists():
            self.add_font("Latin", "", str(latin_regular))
            self.add_font("Latin", "B", str(latin_bold if latin_bold.exists() else latin_regular))
        if mal_regular.exists():
            self.add_font("Mal", "", str(mal_regular))
            self.add_font("Mal", "B", str(mal_bold if mal_bold.exists() else mal_regular))
            self.set_fallback_fonts(["Mal"])
        self.set_text_shaping(True)  # needed for correct Malayalam conjuncts

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(*LINE)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_font("Latin", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "Thank you for your purchase!  |  നന്ദി, വീണ്ടും വരിക", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R")


def money(value: float) -> str:
    return f"₹ {value:,.2f}"


def generate_bill_pdf(bill_id: int, items: list[dict], discount: float, total: float) -> bytes:
    pdf = BillPDF()
    pdf.add_page()

    # ── Header band ──────────────────────────────────────────
    pdf.set_fill_color(*BRAND)
    pdf.rect(0, 0, 210, 34, style="F")
    pdf.set_xy(15, 9)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Latin", "B", 22)
    pdf.cell(110, 10, "Kadakaran")
    pdf.set_font("Latin", "B", 14)
    pdf.cell(70, 10, "INVOICE", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("Latin", "", 10)
    pdf.cell(110, 6, "കടക്കാരൻ")

    # ── Bill meta ────────────────────────────────────────────
    pdf.set_y(42)
    pdf.set_text_color(*DARK)
    pdf.set_font("Latin", "B", 11)
    pdf.cell(90, 7, f"Bill No: #{bill_id}")
    pdf.set_font("Latin", "", 10)
    pdf.set_text_color(*MUTED)
    pdf.cell(90, 7, datetime.now().strftime("Date: %d %b %Y, %I:%M %p"),
             align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Items table ──────────────────────────────────────────
    pdf.set_text_color(*DARK)
    pdf.set_draw_color(*LINE)
    pdf.set_font("Latin", "", 10)

    with pdf.table(
        col_widths=(8, 82, 18, 32, 40),
        text_align=("CENTER", "LEFT", "CENTER", "RIGHT", "RIGHT"),
        headings_style=FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=BRAND),
        borders_layout="HORIZONTAL_LINES",
        cell_fill_color=ZEBRA,
        cell_fill_mode="ROWS",
        line_height=8,
        padding=(1.5, 2),
    ) as table:
        header = table.row()
        for h in ("#", "Item", "Qty", "Price", "Total"):
            header.cell(h)

        for i, item in enumerate(items, start=1):
            qty, price = item["quantity"], item["price"]
            row = table.row()
            row.cell(str(i))
            row.cell(str(item["name"]))      # wraps automatically for long Malayalam names
            row.cell(str(qty))
            row.cell(money(price))
            row.cell(money(qty * price))

    # ── Totals block ─────────────────────────────────────────
    pdf.ln(6)
    if pdf.get_y() > 240:          # keep totals from being orphaned
        pdf.add_page()

    subtotal = sum(i["quantity"] * i["price"] for i in items)
    x_label, w_label, w_value = 115, 40, 40

    def total_row(label, value, bold=False, fill=False, color=DARK, size=10):
        pdf.set_x(x_label)
        pdf.set_font("Latin", "B" if bold else "", size)
        pdf.set_text_color(*color)
        if fill:
            pdf.set_fill_color(*BRAND)
        pdf.cell(w_label, 9, label, fill=fill, align="L")
        pdf.cell(w_value, 9, value, fill=fill, align="R", new_x="LMARGIN", new_y="NEXT")

    total_row("Subtotal", money(subtotal))
    total_row("Discount", f"- {money(discount)}", color=(200, 50, 50))
    pdf.ln(1)
    total_row("TOTAL", money(total), bold=True, fill=True, color=(255, 255, 255), size=12)

    return bytes(pdf.output())