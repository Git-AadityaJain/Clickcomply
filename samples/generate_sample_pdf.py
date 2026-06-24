#!/usr/bin/env python3
"""Generate sample DPDP privacy policy PDF from markdown source."""

from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF

SAMPLES_DIR = Path(__file__).resolve().parent
MD_PATH = SAMPLES_DIR / "ClickComply_Sample_DPDP_Privacy_Policy.md"
PDF_PATH = SAMPLES_DIR / "ClickComply_Sample_DPDP_Privacy_Policy.pdf"


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2192", "->")


def safe(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def writeln(pdf: FPDF, text: str, h: float = 5) -> None:
    pdf.set_x(pdf.l_margin)
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.multi_cell(w, h, safe(strip_md(text)))


def build_pdf() -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(18, 18, 18)

    for line in MD_PATH.read_text(encoding="utf-8").splitlines():
        raw = line.rstrip()
        if not raw.strip():
            pdf.ln(3)
            continue

        if raw.startswith("|"):
            if re.match(r"^\|[-: |]+\|$", raw.replace(" ", "")):
                continue
            cells = [c.strip() for c in raw.strip("|").split("|")]
            pdf.set_font("Helvetica", "", 9)
            writeln(pdf, " | ".join(cells))
            continue

        if raw.startswith("# "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 16)
            writeln(pdf, raw[2:], h=7)
        elif raw.startswith("## "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 13)
            writeln(pdf, raw[3:], h=6)
        elif raw.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            writeln(pdf, raw[4:])
        elif raw.startswith("- "):
            pdf.set_font("Helvetica", "", 9)
            writeln(pdf, "  - " + raw[2:])
        elif raw.startswith("---"):
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", "", 9)
            writeln(pdf, raw)

    pdf.output(str(PDF_PATH))
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
