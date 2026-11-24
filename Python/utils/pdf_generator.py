import os
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def hex_to_color(hex_str, default=colors.HexColor("#6366f1")):
    """Safely converts hex string to ReportLab Color."""
    try:
        if hex_str and hex_str.startswith("#") and len(hex_str) in [4, 7]:
            return colors.HexColor(hex_str)
        return default
    except Exception:
        return default

def generate_resume_pdf(resume_data, template="modern", output_stream=None):
    """
    Generates a high-quality, professional, printable A4 PDF for any of the 5 templates:
    1. modern: Modern Professional (clean colored accent bar, headers, elegant layout)
    2. minimal: Minimal Clean (timeless classic typography, subtle separators, high ATS readability)
    3. corporate: Corporate Executive (structured, bold headings, formal divider bars)
    4. creative: Creative Dynamic (vibrant section badges, modern spacing)
    5. technical: Developer / Technical (compact, emphasis on tech stack, skills table, project links)
    """
    if output_stream is None:
        output_stream = io.BytesIO()

    # Document setup: A4 with 0.5 in margins for maximum content space
    doc = SimpleDocTemplate(
        output_stream,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Theme accents
    accent_hex = resume_data.get('accent_color', '#6366f1')
    accent_col = hex_to_color(accent_hex)
    dark_gray = colors.HexColor("#1e293b")
    med_gray = colors.HexColor("#64748b")
    light_border = colors.HexColor("#e2e8f0")

    # Typography styles
    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=accent_col if template in ['creative', 'modern'] else dark_gray,
        alignment=TA_CENTER if template in ['minimal', 'corporate'] else TA_LEFT
    )

    title_style = ParagraphStyle(
        'ResumeTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=med_gray,
        alignment=TA_CENTER if template in ['minimal', 'corporate'] else TA_LEFT
    )

    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=dark_gray,
        alignment=TA_CENTER if template in ['minimal', 'corporate'] else TA_LEFT
    )

    section_heading_style = ParagraphStyle(
        'ResumeSectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=accent_col if template != 'minimal' else dark_gray,
        spaceAfter=4,
        spaceBefore=8,
        textTransform='uppercase'
    )

    item_title_style = ParagraphStyle(
        'ResumeItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=dark_gray
    )

    item_subtitle_style = ParagraphStyle(
        'ResumeItemSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=med_gray
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_gray
    )

    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        leftIndent=12,
        textColor=dark_gray
    )

    # 1. Personal Header
    p = resume_data.get('personal_info', {})
    full_name = p.get('full_name') or 'Candidate Name'
    prof_title = p.get('professional_title') or resume_data.get('target_role') or ''
    
    story.append(Paragraph(full_name, name_style))
    if prof_title:
        story.append(Spacer(1, 2))
        story.append(Paragraph(prof_title, title_style))

    # Contact Info line
    contact_parts = []
    if p.get('email'): contact_parts.append(p['email'])
    if p.get('phone'): contact_parts.append(p['phone'])
    if p.get('location'): contact_parts.append(p['location'])
    if p.get('linkedin_url'): contact_parts.append("LinkedIn: " + p['linkedin_url'])
    if p.get('github_url'): contact_parts.append("GitHub: " + p['github_url'])
    if p.get('portfolio_url'): contact_parts.append("Portfolio: " + p['portfolio_url'])

    if contact_parts:
        story.append(Spacer(1, 4))
        story.append(Paragraph(" • ".join(contact_parts), contact_style))

    story.append(Spacer(1, 6))
    divider_color = accent_col if template in ['modern', 'corporate'] else light_border
    story.append(HRFlowable(width="100%", thickness=1.5 if template == 'corporate' else 1, color=divider_color, spaceAfter=8, spaceBefore=4))

    # Helper function to add standard section headers
    def add_section_header(title):
        story.append(Paragraph(title, section_heading_style))
        if template in ['modern', 'corporate', 'technical']:
            story.append(HRFlowable(width="100%", thickness=0.75, color=accent_col if template != 'corporate' else dark_gray, spaceAfter=6, spaceBefore=2))
        else:
            story.append(Spacer(1, 4))

    # 2. Professional Summary
    summary = p.get('summary')
    if summary and summary.strip():
        add_section_header("Professional Summary")
        story.append(Paragraph(summary.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 6))

    # 3. Work Experience
    experiences = resume_data.get('work_experience', [])
    if experiences:
        add_section_header("Work Experience")
        for exp in experiences:
            comp = exp.get('company_name', '')
            role = exp.get('job_title', '')
            emp_type = f" ({exp.get('employment_type')})" if exp.get('employment_type') else ""
            dates = f"{exp.get('start_date', '')} – {exp.get('end_date', 'Present') if not exp.get('is_current') else 'Present'}"
            
            # 2-column header row: Job Title + Company on Left, Dates on Right
            left_text = f"<b>{role}</b> – {comp}{emp_type}"
            right_text = f"<b>{dates}</b>"
            
            exp_table = Table(
                [[Paragraph(left_text, item_title_style), Paragraph(right_text, ParagraphStyle('RightDate', parent=item_subtitle_style, alignment=TA_RIGHT))]],
                colWidths=[380, 140]
            )
            exp_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(exp_table)
            
            # Responsibilities / Achievements
            resp = exp.get('responsibilities', '')
            if resp:
                for line in resp.strip().split('\n'):
                    clean_line = line.strip()
                    if clean_line:
                        if not clean_line.startswith(('•', '-', '*')):
                            clean_line = f"• {clean_line}"
                        story.append(Paragraph(clean_line, bullet_style))
                        
            achieve = exp.get('achievements', '')
            if achieve:
                for line in achieve.strip().split('\n'):
                    clean_line = line.strip()
                    if clean_line:
                        if not clean_line.startswith(('•', '-', '*')):
                            clean_line = f"• Key Achievement: {clean_line}"
                        story.append(Paragraph(clean_line, bullet_style))
                        
            story.append(Spacer(1, 6))

    # 4. Education
    educations = resume_data.get('education', [])
    if educations:
        add_section_header("Education")
        for edu in educations:
            inst = edu.get('institution_name', '')
            deg = edu.get('degree', '')
            field = f" in {edu.get('field_of_study')}" if edu.get('field_of_study') else ""
            dates = f"{edu.get('start_year', '')} – {edu.get('graduation_year', '')}"
            grade = f" | Grade/CGPA: {edu.get('grade')}" if edu.get('grade') else ""

            left_text = f"<b>{deg}{field}</b><br/>{inst}{grade}"
            right_text = f"<b>{dates}</b>"
            
            edu_table = Table(
                [[Paragraph(left_text, item_title_style), Paragraph(right_text, ParagraphStyle('RightDateEdu', parent=item_subtitle_style, alignment=TA_RIGHT))]],
                colWidths=[400, 120]
            )
            edu_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(edu_table)
            story.append(Spacer(1, 4))

    # 5. Skills
    skills = resume_data.get('skills', [])
    if skills:
        add_section_header("Skills & Competencies")
        by_category = {}
        for s in skills:
            cat = s.get('category', 'technical').capitalize()
            by_category.setdefault(cat, []).append(s.get('name', ''))
            
        for cat, items in by_category.items():
            skill_line = f"<b>{cat}:</b> " + ", ".join(items)
            story.append(Paragraph(skill_line, body_style))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 4))

    # 6. Projects
    projects = resume_data.get('projects', [])
    if projects:
        add_section_header("Key Projects")
        for proj in projects:
            p_name = proj.get('project_name', '')
            tech = f" (Technologies: {proj.get('technologies')})" if proj.get('technologies') else ""
            url = f" — <font color='{accent_hex}'>{proj.get('project_url')}</font>" if proj.get('project_url') else ""
            
            story.append(Paragraph(f"<b>{p_name}</b>{tech}{url}", item_title_style))
            if proj.get('description'):
                story.append(Paragraph(proj['description'].replace("\n", " "), body_style))
            story.append(Spacer(1, 4))

    # 7. Certifications & Languages (Side by side or stacked)
    certs = resume_data.get('certifications', [])
    langs = resume_data.get('languages', [])

    if certs:
        add_section_header("Certifications")
        for cert in certs:
            c_name = cert.get('certification_name', '')
            issuer = f" – {cert.get('issuing_org')}" if cert.get('issuing_org') else ""
            dt = f" ({cert.get('issue_date')})" if cert.get('issue_date') else ""
            c_url = f" [<font color='{accent_hex}'>Link</font>]" if cert.get('certificate_url') else ""
            story.append(Paragraph(f"• <b>{c_name}</b>{issuer}{dt}{c_url}", body_style))
        story.append(Spacer(1, 4))

    if langs:
        add_section_header("Languages")
        lang_items = [f"<b>{l.get('language_name')}</b> ({l.get('proficiency_level', 'Proficient')})" for l in langs]
        story.append(Paragraph(" • ".join(lang_items), body_style))
        story.append(Spacer(1, 4))

    # Build PDF document
    doc.build(story)
    output_stream.seek(0)
    return output_stream

def generate_cover_letter_pdf(letter_data, user_name="Candidate", output_stream=None):
    """
    Generates a clean, formatted PDF for a cover letter.
    """
    if output_stream is None:
        output_stream = io.BytesIO()

    doc = SimpleDocTemplate(
        output_stream,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    story = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        'CoverHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e293b")
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b")
    )

    body_style = ParagraphStyle(
        'CoverBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12
    )

    story.append(Paragraph(user_name, header_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Target Role: {letter_data.get('job_title', 'Role')} | {letter_data.get('company_name', 'Company')}", meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=16, spaceBefore=4))

    content = letter_data.get('content', '')
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", "<br/>"), body_style))

    doc.build(story)
    output_stream.seek(0)
    return output_stream
