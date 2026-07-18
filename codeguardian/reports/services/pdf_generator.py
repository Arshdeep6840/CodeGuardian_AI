from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(scan):
    """
    Generate a styled PDF code health report for a scan using ReportLab.
    Returns the raw PDF byte content.
    """
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    
    # Standard styles
    styles = getSampleStyleSheet()
    
    # Custom Color Scheme (matching index.html premium aesthetics)
    primary_color = colors.HexColor("#7365F0")
    dark_bg = colors.HexColor("#0B1222")
    text_color = colors.HexColor("#1D253D")
    
    critical_color = colors.HexColor("#FF3B5C")
    high_color = colors.HexColor("#FF8A3E")
    medium_color = colors.HexColor("#FFC53D")
    low_color = colors.HexColor("#23D18B")
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=primary_color,
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=dark_bg,
        spaceBefore=14,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=text_color,
        leading=12,
        spaceAfter=6
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    # 1. Document Title & Details
    story.append(Paragraph("CodeGuardian AI Security & Health Report", title_style))
    story.append(Paragraph(f"<b>Project Name:</b> {scan.project.name}", body_style))
    story.append(Paragraph(f"<b>Scan Configuration:</b> {scan.scan_name} | <b>Date:</b> {scan.created_at.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 10))
    
    # 2. Score Metrics Table
    summary_data = [
        [Paragraph("Metric", header_style), Paragraph("Score / Counts", header_style)],
        ["Security Rating Score", f"{scan.security_score}%"],
        ["Code Quality Score", f"{scan.code_quality_score}%"],
        ["Maintainability Score", f"{scan.maintainability_score}%"],
        ["Overall Project Health Score", f"{scan.overall_score}%"],
        ["Total Files Analyzed", str(scan.total_files_scanned)],
        ["Total Issues Detected", str(scan.total_issues_found)],
        ["Critical Severity Issues", str(scan.critical_issues)],
        ["High Severity Issues", str(scan.high_issues)],
        ["Medium Severity Issues", str(scan.medium_issues)],
        ["Low Severity Issues", str(scan.low_issues)],
    ]
    
    summary_table = Table(summary_data, colWidths=[240, 160])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#FAFAFA"), colors.white]),
        ('PADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # 3. Scanned Issues Detailed Table
    story.append(Paragraph("Scanned Issues Breakdown", h2_style))
    
    issues = scan.issues.all()
    if not issues.exists():
        story.append(Paragraph("No issues found in this project. Clean build!", body_style))
    else:
        issues_data = [
            [Paragraph("Severity", header_style), 
             Paragraph("Location", header_style), 
             Paragraph("Description", header_style)]
        ]
        
        # Display up to 50 issues to avoid rendering overly massive documents
        for issue in issues[:50]:
            sev_text = issue.severity.upper()
            if issue.severity == "critical":
                sev_p = Paragraph(f"<font color='{critical_color.hexval()}'><b>{sev_text}</b></font>", body_style)
            elif issue.severity == "high":
                sev_p = Paragraph(f"<font color='{high_color.hexval()}'><b>{sev_text}</b></font>", body_style)
            elif issue.severity == "medium":
                sev_p = Paragraph(f"<font color='{medium_color.hexval()}'><b>{sev_text}</b></font>", body_style)
            else:
                sev_p = Paragraph(f"<font color='{low_color.hexval()}'><b>{sev_text}</b></font>", body_style)
                
            loc_text = f"{issue.file_path}:{issue.line_number or 1}"
            desc_text = issue.title
            
            issues_data.append([
                sev_p,
                Paragraph(loc_text, body_style),
                Paragraph(desc_text, body_style)
            ])
            
        issues_table = Table(issues_data, colWidths=[70, 150, 310])
        issues_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), dark_bg),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(issues_table)
        
        if issues.count() > 50:
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<i>* Note: Displaying first 50 issues out of {issues.count()} total. View the dashboard to review all issues.</i>", body_style))
            
    # Build Document
    doc.build(story)
    
    # Retrieve bytes from buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
