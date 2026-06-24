"""Export compliance review results as a PDF report."""

from __future__ import annotations

from datetime import datetime, timezone

try:
    from fpdf import FPDF

    _HAS_FPDF = True
except ImportError:
    _HAS_FPDF = False


def _safe_text(text: str) -> str:
    """FPDF core fonts are latin-1; replace unsupported characters."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def export_review_pdf(document_name: str, analysis: dict) -> bytes:
    if not _HAS_FPDF:
        raise RuntimeError("PDF export is not available on this server.")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 8, _safe_text("ClickComply Review Report"))
    pdf.ln(4)

    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 5, _safe_text(f"Document: {document_name}"))
    pdf.multi_cell(
        0,
        5,
        _safe_text(
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        ),
    )
    pdf.ln(3)

    status = analysis.get("overall_status", "UNKNOWN")
    pdf.set_font("Helvetica", "B", 11)
    pdf.multi_cell(0, 6, _safe_text(f"Overall status: {status}"))
    pdf.ln(2)

    note = analysis.get("note", "")
    if note:
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, _safe_text(note))
        pdf.ln(3)

    rules = analysis.get("rules_evaluated")
    if rules is not None:
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, _safe_text(f"Rules checked: {rules}"))
        pdf.ln(3)

    gaps = analysis.get("identified_gaps") or []
    if gaps:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 6, _safe_text("Compliance gaps"))
        pdf.ln(2)
        pdf.set_font("Helvetica", size=10)
        for i, gap in enumerate(gaps, 1):
            section = gap.get("section", "General")
            severity = gap.get("severity", "")
            desc = gap.get("description", "")
            pdf.multi_cell(
                0,
                5,
                _safe_text(f"{i}. [{severity}] {section}: {desc}"),
            )
            pdf.ln(2)
        pdf.ln(2)

    recs = analysis.get("recommendations") or []
    if recs:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 6, _safe_text("Recommendations"))
        pdf.ln(2)
        pdf.set_font("Helvetica", size=10)
        for i, rec in enumerate(recs, 1):
            section = rec.get("section", "General")
            priority = rec.get("priority", "")
            action = rec.get("action", "")
            pdf.multi_cell(
                0,
                5,
                _safe_text(f"{i}. [{priority}] {section}: {action}"),
            )
            pdf.ln(2)

    if not gaps and not recs:
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, _safe_text("No gaps or recommendations recorded for this review."))

    out = pdf.output()
    return out if isinstance(out, bytes) else out.encode("latin-1")
