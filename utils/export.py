from fpdf import FPDF
import io

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Contract Risk Assessment Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_report(analysis_result, contract_type="Unknown"):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # helper for clean text
    s = sanitize_text
    
    # 1. Summary Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, s(f"Contract Type: {contract_type}"), 0, 1)
    
    score = analysis_result.get('overall_risk_score', 0)
    pdf.cell(0, 10, s(f"Risk Score: {score}/100"), 0, 1)
    
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, s(f"Executive Summary: {analysis_result.get('summary', 'No summary available.')}"))
    pdf.ln(5)
    
    # 2. Risk Findings
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Risk Assessment:", 0, 1)
    
    pdf.set_font("Arial", '', 10)
    for clause in analysis_result.get('clauses', []):
        risk = clause.get('risk_level', 'Low')
        
        # Color coding attempt (simple bolding for High)
        title_prefix = "[HIGH RISK]" if risk == "High" else f"[{risk} Risk]"
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, s(f"{title_prefix} {clause.get('title')}"), 0, 1)
        
        pdf.set_font("Arial", 'I', 9)
        pdf.multi_cell(0, 5, s(f"Clause: \"{clause.get('text')[:200]}...\""))
        
        pdf.set_font("Arial", '', 9)
        pdf.multi_cell(0, 5, s(f"Analysis: {clause.get('explanation')}"))
        pdf.multi_cell(0, 5, s(f"Recommendation: {clause.get('recommendation')}"))
        
        # Add Citation if present
        if clause.get('citation'):
             pdf.multi_cell(0, 5, s(f"Legal Ref: {clause.get('citation')}"))
             
        pdf.ln(3)

    # 3. Missing Clauses
    if analysis_result.get('missing_clauses'):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "Missing Protective Clauses:", 0, 1)
        pdf.set_font("Arial", '', 10)
        for missing in analysis_result.get('missing_clauses'):
             pdf.cell(0, 6, s(f"- {missing}"), 0, 1)

    # Return bytes
    # FPDF's output() returns a latin-1 string in Py3. 
    # Attempting to encode it again to latin-1 fails if we inserted unicode chars it couldn't map.
    # We must sanitize INPUTS before adding to FPDF, or use a font that supports it (but we don't have one loaded).
    # Simple fix: Return the bytearray directly if possible, or handle encoding safe.
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def sanitize_text(text):
    """
    Replaces non-latin-1 characters to prevent FPDF crash.
    """
    if not text: return ""
    return text.encode('latin-1', 'replace').decode('latin-1')

# Monkey-patch FPDF cell/multi_cell if needed, or just sanitize inputs below
# Let's wrap the logic above to use sanitize_text

