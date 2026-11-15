"""PDF "site feasibility report" for one analog pair (Moon or Mars site vs an Earth place).

Turns the app's profile into a document a planetary geologist can file or share: match per aspect, reliability of the method,
how robust the rank is, field-site risk indicators, where the analogy breaks down, the two orbital views and credits.
It uses only the core PDF fonts (Latin-1), so text is sanitised before writing.
"""
import io

from fpdf import FPDF

from .i18n import t

_REPLACE = {"≈": "~", "−": "-", "–": "-", "—": "-", "·": "-", "≥": ">=", "≤": "<=", "→": "->", "●": "*", "µ": "u", "³": "3",
            "’": "'", "“": '"', "”": '"', "×": "x", "…": "..."}
ORANGE, DARK, GREY = (255, 140, 66), (30, 36, 50), (110, 118, 130)
LEVEL_RGB = {"low": (30, 160, 110), "medium": (200, 140, 10), "high": (210, 60, 60), "unknown": (120, 128, 140)}


def clean(text) -> str:
    """Latin-1 safe text: common symbols are replaced, anything else outside Latin-1 becomes '?'."""
    s = str(text)
    for a, b in _REPLACE.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


class _Pdf(FPDF):
    def __init__(self, footer_text: str):
        super().__init__(format="A4")
        self.footer_text = clean(footer_text)
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(16, 16, 16)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, f"{self.footer_text}  -  {self.page_no()}", align="C")


def _h2(pdf: _Pdf, text: str):
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*ORANGE)
    pdf.cell(0, 7, clean(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*ORANGE)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)
    pdf.set_text_color(*DARK)


def _p(pdf: _Pdf, text: str, size: int = 10, style: str = "", color=DARK, h: float = 5):
    pdf.set_font("Helvetica", style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, h, clean(text), new_x="LMARGIN", new_y="NEXT")


def _row(pdf: _Pdf, cells: list[tuple[str, float, tuple | None]], h: float = 6, bold: bool = False):
    """One table row: (text, width, rgb colour or None)."""
    y0 = pdf.get_y()
    for text, w, rgb in cells:
        pdf.set_font("Helvetica", "B" if (bold or rgb) else "", 9)
        pdf.set_text_color(*(rgb or DARK))
        pdf.cell(w, h, clean(text)[:70], new_x="RIGHT", new_y="TOP")
    pdf.set_xy(pdf.l_margin, y0 + h)
    pdf.set_text_color(*DARK)


def build_report(d: dict, lang: str = "en") -> bytes:
    """Build the PDF from a plain dict (see `tests/test_report_pdf.py` for the fields) and return its bytes."""
    pdf = _Pdf(t(lang, "pdf_generado", fecha=d["date"]))
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 9, "AstroAtlas", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 6, clean(t(lang, "pdf_titulo")), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    _p(pdf, f"{d['place']} ({d['country']})", 15, "B")
    _p(pdf, f"{d['coords']}  -  {d['terrain']}", 9, "", GREY)
    pdf.ln(1)
    _p(pdf, t(lang, "pdf_resumen", lugar=d["place"], pais=d["country"], sitio=d["site"], cuerpo=d["body_name"], n=d["match_pct"],
              k=d["n_aspects"], total=d["n_total"]), 10.5)

    _h2(pdf, t(lang, "pdf_s_aspectos"))
    for a in d["aspects"]:
        score = "-" if a["pct"] is None else f"{a['pct']}%"
        _row(pdf, [(a["name"], 38, None), (score, 16, None), (a["level"], 40, None)], bold=False)
        _p(pdf, a["text"], 8.5, "", GREY, 4.2)
        pdf.ln(1)

    rel = d["reliability"]
    _h2(pdf, t(lang, "pdf_s_confianza"))
    _p(pdf, t(lang, "pdf_confianza", nivel=rel["nivel"], pct=rel["pct"], lo=rel["lo"], hi=rel["hi"], n=rel["n"]))
    _p(pdf, rel["texto"], 9, "", GREY)

    sens = d.get("sensitivity")
    if sens:
        _h2(pdf, t(lang, "pdf_s_sens"))
        _p(pdf, sens["summary"], 9.5)
        pdf.ln(1)
        _row(pdf, [(t(lang, "sens_col_escenario"), 62, None), (t(lang, "sens_col_puesto"), 22, None), (t(lang, "sens_col_parecido"), 24, None)], bold=True)
        for r in sens["rows"]:
            _row(pdf, [(r["scenario"], 62, None), (r["rank"], 22, None), (r["score"], 24, None)])

    _h2(pdf, t(lang, "pdf_s_riesgos"))
    _row(pdf, [(t(lang, "riesgo_general"), 38, None), (d["risk_overall"][0], 30, LEVEL_RGB[d["risk_overall"][1]])], bold=True)
    for r in d["risks"]:
        _row(pdf, [(r["name"], 38, None), (r["level_text"], 30, LEVEL_RGB[r["level"]]), (r["value"], 100, None)])
    if d.get("target_risk"):
        pdf.ln(1)
        _p(pdf, d["target_risk"], 9)
    _p(pdf, t(lang, "riesgo_nota"), 8.5, "I", GREY, 4.2)
    _p(pdf, t(lang, "riesgo_no_evaluado"), 8.5, "B", DARK, 4.2)

    _h2(pdf, t(lang, "pdf_s_limites"))
    for item in d["limits"]:
        _p(pdf, f"- {item}", 9, "", DARK, 4.6)

    _h2(pdf, t(lang, "pdf_s_imagenes"))
    w = (pdf.w - pdf.l_margin - pdf.r_margin - 6) / 2
    if pdf.get_y() + w + 22 > pdf.h - 18:
        pdf.add_page()
    y = pdf.get_y()
    for i, (img, cap, cred) in enumerate(d["images"]):
        x = pdf.l_margin + i * (w + 6)
        if img:
            pdf.image(io.BytesIO(img), x=x, y=y, w=w, h=w)
        else:
            pdf.set_xy(x, y + w / 2)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*GREY)
            pdf.cell(w, 6, clean(t(lang, "pdf_sin_imagen")), align="C")
        pdf.set_xy(x, y + w + 1)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(w, 4, clean(cap), new_x="LEFT", new_y="NEXT")
        pdf.set_x(x)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*GREY)
        pdf.multi_cell(w, 3.6, clean(cred), new_x="LEFT", new_y="NEXT")
    pdf.set_xy(pdf.l_margin, y + w + 20)

    _h2(pdf, t(lang, "pdf_s_creditos"))
    _p(pdf, t(lang, "pdf_aviso"), 8.5, "", GREY, 4.2)
    return bytes(pdf.output())
