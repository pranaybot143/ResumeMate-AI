from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2463A6")
LIGHT_BLUE = colors.HexColor("#EAF2F8")
LIGHT_GREY = colors.HexColor("#F3F5F7")
MID_GREY = colors.HexColor("#5B6573")
DARK = colors.HexColor("#202833")
GREEN = colors.HexColor("#247A52")
RED = colors.HexColor("#B54747")


def _safe(value):
    return escape(str(value if value is not None else ""))


def _shorten(text, max_chars=220):
    """Keep report text concise without changing its meaning."""
    text = " ".join(str(text).split())
    if len(text) <= max_chars:
        return text
    shortened = text[:max_chars].rsplit(" ", 1)[0]
    return shortened.rstrip(" ,;:-") + "..."


def _compact_list(items, limit=3, max_chars=150):
    """Select only a few concise points for the summary report."""
    if not isinstance(items, list):
        return []
    result = []
    for item in items:
        if isinstance(item, str) and item.strip():
            result.append(_shorten(item.strip(), max_chars))
        if len(result) >= limit:
            break
    return result


def _bullet_paragraphs(items, styles, limit=3, max_chars=150):
    if not items:
        return [Paragraph("Not available.", styles["Body"])]
    return [
        Paragraph(
            f'<font color="{BLUE.hexval()}">&#8226;</font>  {_safe(item)}',
            styles["Body"]
        )
        for item in _compact_list(items, limit, max_chars)
    ]


def _header_footer(canvas, document):
    canvas.saveState()
    width, height = A4

    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 13 * mm, width, 13 * mm, fill=1, stroke=0)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(18 * mm, height - 8.5 * mm, "RESUMEMATE AI")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawRightString(width - 18 * mm, height - 8.5 * mm, "RESUME ANALYSIS SUMMARY")

    canvas.setStrokeColor(colors.HexColor("#D9DEE5"))
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFillColor(MID_GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, 8 * mm, "Automated analysis — review results before making career decisions")
    canvas.drawRightString(width - 18 * mm, 8 * mm, f"Page {document.page}")
    canvas.restoreState()


def generate_report(data, resume_filename):
    """
    Generate a concise summary report (normally 1–2 pages).
    Gemini content is summarised by limiting the number and length of points.
    """

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="ResumeMate AI - Resume Analysis Summary",
        author="ResumeMate AI",
    )

    sample = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "ReportTitle", parent=sample["Title"],
            fontName="Helvetica-Bold", fontSize=18, leading=21,
            alignment=TA_CENTER, textColor=NAVY, spaceAfter=3,
        ),
        "Sub": ParagraphStyle(
            "Sub", parent=sample["Normal"], fontSize=8,
            leading=10, textColor=MID_GREY, alignment=TA_CENTER,
        ),
        "Section": ParagraphStyle(
            "Section", parent=sample["Heading2"],
            fontName="Helvetica-Bold", fontSize=10.5, leading=13,
            textColor=NAVY, spaceBefore=8, spaceAfter=4,
            keepWithNext=True,
        ),
        "Subheading": ParagraphStyle(
            "Subheading", parent=sample["Heading3"],
            fontName="Helvetica-Bold", fontSize=8.5, leading=10,
            textColor=BLUE, spaceBefore=4, spaceAfter=2,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "Body", parent=sample["BodyText"],
            fontName="Helvetica", fontSize=8, leading=10.5,
            textColor=DARK, spaceAfter=2,
        ),
        "Small": ParagraphStyle(
            "Small", parent=sample["Normal"],
            fontSize=7, leading=9, textColor=MID_GREY,
        ),
        "Metric": ParagraphStyle(
            "Metric", parent=sample["Normal"],
            fontName="Helvetica-Bold", fontSize=15, leading=17,
            alignment=TA_CENTER, textColor=NAVY,
        ),
        "MetricLabel": ParagraphStyle(
            "MetricLabel", parent=sample["Normal"],
            fontSize=7, leading=8, alignment=TA_CENTER,
            textColor=MID_GREY,
        ),
    }

    content = [
        Spacer(1, 2 * mm),
        Paragraph("Resume Analysis Summary", styles["Title"]),
        Paragraph(f"Resume: {_safe(resume_filename)}", styles["Sub"]),
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#D9E2EC")),
        Spacer(1, 3 * mm),
    ]

    # Compact score cards
    score = data.get("score", "N/A")
    coverage = data.get("skill_coverage")
    score_text = f"{score}%" if isinstance(score, (int, float)) else str(score)
    coverage_text = f"{coverage}%" if coverage is not None else "N/A"

    metrics = Table(
        [[
            Paragraph("SEMANTIC MATCH", styles["MetricLabel"]),
            Paragraph("SKILL COVERAGE", styles["MetricLabel"]),
        ], [
            Paragraph(_safe(score_text), styles["Metric"]),
            Paragraph(_safe(coverage_text), styles["Metric"]),
        ]],
        colWidths=[document.width / 2] * 2,
        rowHeights=[7 * mm, 12 * mm],
    )
    metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5E2EE")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    content.append(metrics)
    content.append(Paragraph(
        "These are separate indicators, not hiring probabilities.",
        styles["Small"]
    ))

    # Skill comparison
    content.append(Paragraph("Skill Comparison", styles["Section"]))
    matching = data.get("matching_skills", [])
    missing = data.get("missing_skills", [])

    def skills_text(items, empty):
        if not items:
            return empty
        return "<br/>".join(f"&#8226; {_safe(x)}" for x in items[:12])

    comparison = Table(
        [[
            Paragraph("<b>Matching</b>", styles["Body"]),
            Paragraph("<b>Missing</b>", styles["Body"]),
        ], [
            Paragraph(skills_text(matching, "None identified"), styles["Body"]),
            Paragraph(skills_text(missing, "None identified"), styles["Body"]),
        ]],
        colWidths=[document.width / 2] * 2,
    )
    comparison.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#EAF5EF")),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#FBEFEF")),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9DEE5")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    content.append(comparison)

    # Short Gemini summary
    feedback = data.get("ai_feedback", {})
    content.append(Paragraph("AI Feedback Summary", styles["Section"]))

    source = data.get("recommendation_source")
    source_label = "Google Gemini" if source == "gemini" else "Fallback recommendations"
    content.append(Paragraph(f"<b>Source:</b> {_safe(source_label)}", styles["Small"]))

    overall = feedback.get("overall_feedback", "")
    if overall:
        content.append(Paragraph("Overall assessment", styles["Subheading"]))
        content.append(Paragraph(_safe(_shorten(overall, 300)), styles["Body"]))

    summary_sections = [
        ("Key strengths", "strengths", 3, 130),
        ("Priority improvement areas", "improvement_areas", 3, 130),
        ("Learning roadmap", "learning_roadmap", 3, 130),
        ("Suggested projects", "project_suggestions", 2, 130),
        ("Resume tips", "resume_tips", 2, 130),
    ]

    for heading, key, limit, max_chars in summary_sections:
        items = feedback.get(key, [])
        if items:
            content.append(Paragraph(heading, styles["Subheading"]))
            content.extend(_bullet_paragraphs(items, styles, limit, max_chars))

    # Concise skill recommendations
    recommendations = data.get("recommendations", [])
    if recommendations:
        content.append(Paragraph("Priority Skill Recommendations", styles["Section"]))
        for item in recommendations[:5]:
            skill = _safe(item.get("skill", "Skill"))
            recommendation = _safe(_shorten(item.get("recommendation", ""), 150))
            content.append(Paragraph(
                f"<b>{skill}:</b> {recommendation}",
                styles["Body"]
            ))
        if len(recommendations) > 5:
            content.append(Paragraph(
                f"{len(recommendations) - 5} additional recommendations are not shown in this summary.",
                styles["Small"]
            ))

    # Very small evidence sample rather than printing every extracted snippet.
    evidence_items = data.get("resume_skill_evidence", [])
    if evidence_items:
        content.append(Paragraph("Selected Resume Evidence", styles["Section"]))
        for item in evidence_items[:4]:
            skill = _safe(item.get("skill", "Skill"))
            evidence = item.get("evidence", [])
            if evidence:
                first = evidence[0]
                if isinstance(first, dict):
                    section = _safe(first.get("section", "Other"))
                    evidence_text = _safe(_shorten(first.get("text", ""), 115))
                    content.append(Paragraph(
                        f"<b>{skill}</b> ({section}): {evidence_text}",
                        styles["Body"]
                    ))

    warning = data.get("recommendation_warning", "")
    if warning:
        content.append(Spacer(1, 2 * mm))
        content.append(Paragraph(
            f"<font color='#9A5B00'><b>AI notice:</b> {_safe(_shorten(warning, 180))}</font>",
            styles["Small"]
        ))

    content.extend([
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D9DEE5")),
        Spacer(1, 2 * mm),
        Paragraph(
            "<b>Disclaimer:</b> This report provides automated text analysis "
            "and AI-generated guidance. Skill mentions and semantic similarity "
            "may not fully represent a candidate's actual proficiency. "
            "Results are informational and are not hiring decisions.",
            styles["Small"]
        ),
    ])

    document.build(
        content,
        onFirstPage=_header_footer,
        onLaterPages=_header_footer
    )

    buffer.seek(0)
    return buffer.getvalue()
