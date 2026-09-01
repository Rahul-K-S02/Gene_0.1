import io
import base64
import logging
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

logger = logging.getLogger("generisk.report_generator")

def generate_pdf_report(
    patient_summary: Dict[str, Any],
    disease_risks: List[Dict[str, Any]],
    clinvar_findings: List[Dict[str, Any]],
    pharmgkb_alerts: List[Dict[str, Any]],
    explanation_narrative: str,
    prescriptions: List[str]
) -> str:
    """
    Generates a multi-page clinical genetic risk assessment PDF in-memory (io.BytesIO)
    and returns it as a Base64-encoded string. Never persists anything to disk.
    """
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1a365d")
    )
    
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4a5568")
    )
    
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2b6cb0"),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2d3748"),
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2d3748"),
        leftIndent=15,
        spaceAfter=4
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#718096"),
        alignment=TA_CENTER
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("<b>GeneRisk</b> — Genomic Risk Intelligence Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} | Confidential Clinical Genetic Profile", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2b6cb0"), spaceBefore=2, spaceAfter=10))

    # 2. Patient & Sample Information Table
    patient_data = [
        [
            Paragraph("<b>Patient Age:</b>", body_style), Paragraph(str(patient_summary.get("age", "N/A")), body_style),
            Paragraph("<b>Biological Sex:</b>", body_style), Paragraph(str(patient_summary.get("sex", "N/A")).capitalize(), body_style)
        ],
        [
            Paragraph("<b>Calculated BMI:</b>", body_style), Paragraph(f"{patient_summary.get('bmi', 'N/A')} kg/m²", body_style),
            Paragraph("<b>Smoking Status:</b>", body_style), Paragraph(str(patient_summary.get("smoking_status", "N/A")).capitalize(), body_style)
        ],
        [
            Paragraph("<b>Blood Pressure:</b>", body_style), Paragraph(f"{patient_summary.get('systolic_bp', '120')} mmHg (SBP)", body_style),
            Paragraph("<b>Physical Activity:</b>", body_style), Paragraph(f"{patient_summary.get('physical_activity', 'N/A')} hrs/wk", body_style)
        ]
    ]
    p_table = Table(patient_data, colWidths=[90, 165, 90, 195])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f7fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 14))

    # 3. Multi-Disease Risk Overview
    story.append(Paragraph("1. Multi-Disease Polygenic Risk & Late-Fusion Summary", h2_style))
    
    risk_headers = [
        Paragraph("<b>Condition / Disease</b>", body_style),
        Paragraph("<b>PRS Percentile</b>", body_style),
        Paragraph("<b>Category</b>", body_style),
        Paragraph("<b>10-Yr Absolute</b>", body_style),
        Paragraph("<b>Attribution (Gen / Life)</b>", body_style),
        Paragraph("<b>Panel SNPs</b>", body_style)
    ]
    
    risk_rows = [risk_headers]
    for d in disease_risks:
        cat = d.get("risk_category", "Average")
        cat_color = "#38a169" if cat == "Low" else "#3182ce" if cat == "Average" else "#dd6b20" if cat == "Elevated" else "#e53e3e"
        
        risk_rows.append([
            Paragraph(f"<b>{d.get('disease_name', '')}</b>", body_style),
            Paragraph(f"{d.get('prs_percentile', 50):.1f}th %ile", body_style),
            Paragraph(f"<font color='{cat_color}'><b>{cat}</b></font>", body_style),
            Paragraph(f"{d.get('fused_absolute_risk_10yr', 0)*100:.1f}%", body_style),
            Paragraph(f"{d.get('genetic_contribution_pct', 50):.0f}% / {d.get('lifestyle_contribution_pct', 50):.0f}%", body_style),
            Paragraph(f"{d.get('snps_found', 0)}/{d.get('snps_total', 0)} ({d.get('confidence_score', 1.0)*100:.0f}%)", body_style)
        ])
        
    r_table = Table(risk_rows, colWidths=[140, 75, 65, 75, 115, 70])
    r_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ebf8ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(r_table)
    story.append(Spacer(1, 14))

    # 4. Pharmacogenomics & ClinVar High-Impact Variants
    if pharmgkb_alerts or clinvar_findings:
        story.append(Paragraph("2. Pharmacogenomics (PharmGKB) & ClinVar Annotations", h2_style))
        if pharmgkb_alerts:
            story.append(Paragraph("<b>Actionable Drug-Gene Interactions:</b>", body_style))
            for pg in pharmgkb_alerts:
                story.append(Paragraph(
                    f"• <b>{pg.get('drug')} ({pg.get('gene')} - {pg.get('rsid')}):</b> "
                    f"<font color='#c53030'><b>{pg.get('phenotype_category')}</b></font> — {pg.get('clinical_recommendation')} "
                    f"<i>(Evidence: {pg.get('level_of_evidence')})</i>",
                    bullet_style
                ))
            story.append(Spacer(1, 6))

        if clinvar_findings:
            story.append(Paragraph("<b>ClinVar Pathogenic / Likely Pathogenic Variants:</b>", body_style))
            for cv in clinvar_findings:
                story.append(Paragraph(
                    f"• <b>{cv.get('gene')} ({cv.get('rsid')}):</b> {cv.get('phenotype')} "
                    f"— Significance: <b>{cv.get('clinical_significance')}</b> <i>(Accession: {cv.get('accession')})</i>",
                    bullet_style
                ))
            story.append(Spacer(1, 10))

    # 5. AI Evidence-Grounded Explanation & Prescriptions
    story.append(Paragraph("3. Clinical Genomic Evaluation & Narrative", h2_style))
    
    import re
    def md_to_xml(t: str) -> str:
        t = re.sub(r"^#{1,6}\s*", "", t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
        t = re.sub(r"&(?![a-zA-Z]+;)", "&amp;", t)
        return t

    for para in explanation_narrative.split("\n\n"):
        clean_para = md_to_xml(para.strip())
        if clean_para:
            story.append(Paragraph(clean_para, body_style))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Personalized Lifestyle & Risk-Reduction Prescriptions", h2_style))
    for rx in prescriptions:
        clean_rx = md_to_xml(rx.strip())
        story.append(Paragraph(f"• {clean_rx}", bullet_style))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#a0aec0"), spaceBefore=8, spaceAfter=8))
    story.append(Paragraph(
        "<b>Medical Disclaimer:</b> GeneRisk provides polygenic risk scoring and epidemiological estimates for informational, "
        "investigational, and educational purposes only. It does not provide medical diagnoses or prescribe treatment plans. "
        "Genetic risk represents statistical susceptibility, not certainty. Always consult a qualified medical professional.",
        disclaimer_style
    ))

    doc.build(story)
    pdf_buffer.seek(0)
    pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
    return pdf_b64
