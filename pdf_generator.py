from fpdf import FPDF

class AcademicReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(15, 23, 42)
        self.cell(0, 10, 'EduSphere AI Portal - Diagnostic Report', border=False, ln=True, align='C')
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(71, 85, 105)
        self.cell(0, 5, 'Official Academic Trajectory & Intervention Guidance', border=False, ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()} | Generated automatically by EduSphere AI Engine', align='C')

def generate_student_pdf(username, g1, g2, predicted, risk, studytime, absences):
    pdf = AcademicReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Executive Summary Card
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, 35, 190, 45, 'F')
    
    pdf.set_xy(15, 40)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Student User ID: {username}", ln=True)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"First Period Grade (G1): {g1} / 20 | Second Period Grade (G2): {g2} / 20", ln=True)
    pdf.cell(0, 7, f"Predicted Final Performance (G3): {predicted:.2f} / 20", ln=True)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"Assessed Risk Status: {risk}", ln=True)
    pdf.ln(15)

    # Key Input Indicators
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Logged Behavioral Profile Indicators", ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"- Weekly Study Category: Tier {studytime} (out of 4)", ln=True)
    pdf.cell(0, 6, f"- Total School Absences Recorded: {absences} Days", ln=True)
    pdf.ln(10)

    # Actionable Intervention Guidance
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Official Advisory Recommendations", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    if predicted < 10:
        pdf.multi_cell(0, 6, "HIGH RISK ALERT: Immediate intervention recommended. Student should be assigned mandatory tutoring hours, attendance monitoring, and academic advising review.")
    elif predicted < 13:
        pdf.multi_cell(0, 6, "MODERATE PROGRESS: Student is passing but shows vulnerability. Recommend increasing weekly study blocks to >5 hours and reducing unexcused absences.")
    else:
        pdf.multi_cell(0, 6, "OPTIMAL PERFORMANCE: Student is maintaining distinction-level performance trajectory. Continue current academic habits.")

    return bytes(pdf.output())