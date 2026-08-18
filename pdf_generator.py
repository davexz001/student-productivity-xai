from fpdf import FPDF
import io
from datetime import datetime

class AcademicReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=12)
    
    def header(self):
        # Top border line
        self.set_draw_color(79, 70, 229)
        self.set_line_width(2)
        self.line(10, 6, 200, 6)
        
        # Title
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 16, 'EduSphere AI Portal', border=False, ln=True, align='C')
        
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(71, 85, 105)
        self.cell(0, 4, 'Academic Diagnostic Report', border=False, ln=True, align='C')
        self.ln(4)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_y(-11)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(148, 163, 184)
        self.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | Page {self.page_no()}', align='C')


def clean_text(text):
    """Remove emojis and special characters for PDF compatibility"""
    if not text:
        return ""
    text = str(text)
    replacements = {
        '✅': '[OK]',
        '📈': '[UP]',
        '⚠️': '[WARNING]',
        '🎯': '[TARGET]',
        '🔮': '[PREDICT]',
        '🧠': '[AI]',
        '📊': '[DATA]',
        '📋': '[LOG]',
        '🔄': '[SIMULATE]',
        '👤': '[USER]',
        '📝': '[NOTE]',
        '📥': '[DOWNLOAD]',
        '📄': '[DOC]',
        '🎓': '[EDU]',
        '⚙️': '[SETTINGS]',
        '•': '-',
        '\u2022': '-',
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    return text


def add_section_box(pdf, title, content_lines, y_start, compact=False):
    """Add a section with a rectangular box and title"""
    content_lines = [clean_text(str(line)) for line in content_lines]
    title = clean_text(title)
    
    line_height = 5 if compact else 6
    content_height = len(content_lines) * line_height + 4
    box_height = content_height + 20
    
    pdf.set_draw_color(180, 180, 195)
    pdf.set_line_width(0.6)
    pdf.rect(12, y_start, 186, box_height, 'D')
    
    pdf.set_xy(16, y_start + 3)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 7, title, ln=True)
    
    pdf.set_draw_color(210, 210, 220)
    pdf.line(16, y_start + 12, 188, y_start + 12)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(30, 41, 59)
    y = y_start + 16
    for line in content_lines:
        pdf.set_xy(16, y)
        pdf.multi_cell(170, line_height, line, border=0, align='L')
        y += line_height
    
    return box_height + 2


def generate_student_pdf(username, g1, g2, predicted, risk, studytime, absences, failures, goout, health):
    """Generate PDF report for Student"""
    pdf = AcademicReportPDF()
    pdf.add_page()
    
    username_clean = clean_text(username)
    risk_clean = clean_text(risk)
    
    # ===== SECTION 1: Student Summary =====
    pdf.set_fill_color(238, 242, 255)
    pdf.rect(12, 32, 186, 36, 'F')
    
    pdf.set_xy(16, 36)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, f"Student: {username_clean}", ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(16, 44)
    pdf.cell(0, 7, f"G1: {g1}/20    |    G2: {g2}/20", ln=True)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(79, 70, 229)
    pdf.set_xy(16, 52)
    pdf.cell(0, 7, f"Predicted G3: {predicted:.2f}/20", ln=True)
    
    # ===== SECTION 2: Risk Status =====
    y_pos = 74
    risk_color = (34, 197, 94) if predicted >= 14 else (234, 179, 8) if predicted >= 10 else (239, 68, 68)
    pdf.set_fill_color(risk_color[0], risk_color[1], risk_color[2])
    pdf.rect(12, y_pos, 186, 18, 'F')
    
    pdf.set_xy(16, y_pos + 3)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 9, f"RISK STATUS: {risk_clean.upper()}", ln=True)
    
    # ===== SECTION 3: Behavioral Profile =====
    y_pos = 98
    content = [
        f"Study Time: {studytime}/4",
        f"Absences: {absences} days",
        f"Past Failures: {failures}",
        f"Going Out: {goout}/5",
        f"Health Status: {health}/5"
    ]
    box_height = add_section_box(pdf, "Behavioral Profile", content, y_pos, compact=True)
    
    # ===== SECTION 4: Recommendations =====
    y_pos += box_height + 4
    
    if predicted < 10:
        rec_lines = [
            "HIGH RISK - Immediate intervention required:",
            "- Increase study time to 5+ hours/week",
            "- Reduce absences to below 5 days",
            "- Schedule academic counseling session"
        ]
    elif predicted < 14:
        rec_lines = [
            "MODERATE RISK - Student is passing but vulnerable:",
            "- Increase study time to 3-4 hours/week",
            "- Monitor attendance closely",
            "- Consider peer study groups"
        ]
    else:
        rec_lines = [
            "OPTIMAL PERFORMANCE - Student is on track:",
            "- Continue current study habits",
            "- Maintain attendance record",
            "- Explore advanced coursework options"
        ]
    
    add_section_box(pdf, "Recommendations", rec_lines, y_pos, compact=True)

    return bytes(pdf.output(dest='S'))


def generate_counselor_pdf(username, g1, g2, predicted, risk, studytime, absences, failures, goout, health, risk_factors, action_plan):
    """Generate PDF report for Counselor - Compact 1-Page Layout"""
    pdf = AcademicReportPDF()
    pdf.add_page()
    
    username_clean = clean_text(username)
    risk_clean = clean_text(risk)
    risk_factors_clean = clean_text(risk_factors)
    action_plan_clean = clean_text(action_plan)
    
    # ===== SECTION 1: Student Summary =====
    pdf.set_fill_color(238, 242, 255)
    pdf.rect(12, 32, 186, 36, 'F')
    
    pdf.set_xy(16, 36)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, f"Student: {username_clean}", ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(16, 44)
    pdf.cell(0, 7, f"G1: {g1}/20    |    G2: {g2}/20", ln=True)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(79, 70, 229)
    pdf.set_xy(16, 52)
    pdf.cell(0, 7, f"Predicted G3: {predicted:.2f}/20", ln=True)
    
    # ===== SECTION 2: Risk Status =====
    y_pos = 74
    risk_color = (34, 197, 94) if predicted >= 14 else (234, 179, 8) if predicted >= 10 else (239, 68, 68)
    pdf.set_fill_color(risk_color[0], risk_color[1], risk_color[2])
    pdf.rect(12, y_pos, 186, 18, 'F')
    
    pdf.set_xy(16, y_pos + 3)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 9, f"RISK STATUS: {risk_clean.upper()}", ln=True)
    
    # ===== SECTION 3: Behavioral Profile =====
    y_pos = 98
    content = [
        f"Study Time: {studytime}/4",
        f"Absences: {absences} days",
        f"Past Failures: {failures}",
        f"Going Out: {goout}/5",
        f"Health Status: {health}/5"
    ]
    box_height = add_section_box(pdf, "Behavioral Profile", content, y_pos, compact=True)
    
    # ===== SECTION 4: Risk Factors =====
    y_pos += box_height + 4
    if risk_factors_clean and risk_factors_clean != "None identified":
        risk_lines = risk_factors_clean.split(', ')
    else:
        risk_lines = ["None identified"]
    box_height = add_section_box(pdf, "Identified Risk Factors", risk_lines, y_pos, compact=True)
    
    # ===== SECTION 5: Action Plan =====
    y_pos += box_height + 4
    action_lines = action_plan_clean.split('\n') if action_plan_clean else ["No action plan defined"]
    action_lines = [line.strip() for line in action_lines if line.strip()]
    add_section_box(pdf, "Action Plan", action_lines, y_pos, compact=True)

    return bytes(pdf.output(dest='S'))