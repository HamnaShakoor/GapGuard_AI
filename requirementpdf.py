import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf():
    # Ensure directory exists
    os.makedirs("data/requirements", exist_ok=True)
    pdf_filename = "data/requirements/scholarship_requirements_2026.pdf"

    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6
    )
    
    # Fixed: Define custom Subtitle style extending 'Normal'
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )

    content = []

    # Title & Subtitle
    content.append(Paragraph("National AI Excellence Scholarship 2026", title_style))
    content.append(Paragraph("Official Guidelines & Requirements Specification", subtitle_style))
    content.append(Spacer(1, 10))

    # Section 1
    content.append(Paragraph("Section 1: Academic Eligibility", heading_style))
    content.append(Paragraph("1.1 Candidates must maintain a minimum cumulative Grade Point Average (CGPA) of 3.5 on a 4.0 scale.", body_style))
    content.append(Paragraph("1.2 Proof of enrollment in an accredited Computer Science or Artificial Intelligence degree program is mandatory.", body_style))

    # Section 2
    content.append(Paragraph("Section 2: Required Application Documents", heading_style))
    content.append(Paragraph("2.1 Official Academic Transcript showing all coursework completed to date.", body_style))
    content.append(Paragraph("2.2 Comprehensive Curriculum Vitae (CV) outlining relevant technical skills, publications, and projects.", body_style))
    content.append(Paragraph("2.3 Official Letter of Recommendation from a Department Head or Academic Advisor.", body_style))
    content.append(Paragraph("2.4 Personal Statement (500–800 words) detailing research interests and future vision in AI.", body_style))

    # Section 3
    content.append(Paragraph("Section 3: Special Conditions & Thresholds", heading_style))
    content.append(Paragraph("3.1 Applicants with a CGPA between 3.2 and 3.49 require conditional review (Warning Status).", body_style))
    content.append(Paragraph("3.2 Missing mandatory documents will result in an immediate application halt (Missing Status).", body_style))

    doc.build(content)
    print(f"Successfully generated: {pdf_filename}")


if __name__ == "__main__":
    generate_pdf()