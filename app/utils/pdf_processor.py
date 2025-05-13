import os
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from flask import current_app
import uuid

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def create_pdf_summary(pdf_text):
    """Generate a summary of the PDF content using Gemini API."""
    import google.generativeai as genai
    import os

    # Get API key from environment variable
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        api_key = current_app.config.get('GEMINI_API_KEY')

    # Remove quotes if present
    if api_key and api_key.startswith("'") and api_key.endswith("'"):
        api_key = api_key[1:-1]

    # Configure the Gemini API
    genai.configure(api_key=api_key)

    try:
        # Set up the model
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Generate the summary
        prompt = f"""
        Please summarize the following text from a PDF document.
        Focus on the most important topics and key points.
        Organize the summary in a clear, structured format with headings and bullet points where appropriate.

        TEXT:
        {pdf_text[:100000]}  # Limiting text length to avoid token limits
        """

        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error generating summary: {str(e)}"

def generate_summary_pdf(summary_text, original_filename):
    """Generate a PDF with the summary."""
    # Create a unique filename for the summary PDF
    summary_filename = f"summary_{uuid.uuid4()}_{original_filename}"
    summary_path = os.path.join(current_app.config['UPLOAD_FOLDER'], summary_filename)

    # Create the PDF
    doc = SimpleDocTemplate(
        summary_path,
        pagesize=letter,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=18
    )

    styles = getSampleStyleSheet()
    # Check if the style already exists
    if 'Heading1Custom' not in styles:
        styles.add(ParagraphStyle(
            name='Heading1Custom',
            fontSize=16,
            spaceAfter=12
        ))

    # Create the content
    content = []

    # Add title
    title = f"Summary of {original_filename}"
    content.append(Paragraph(title, styles['Heading1Custom'] if 'Heading1Custom' in styles else styles['Heading1']))
    content.append(Spacer(1, 0.25*inch))

    # Add summary text
    # Split by lines to handle formatting
    for line in summary_text.split('\n'):
        if line.strip():
            if line.startswith('#'):  # Handle markdown headings
                content.append(Paragraph(line.replace('#', '').strip(), styles['Heading1Custom'] if 'Heading1Custom' in styles else styles['Heading1']))
            elif line.startswith('-') or line.startswith('*'):  # Handle bullet points
                content.append(Paragraph(f"• {line[1:].strip()}", styles['Normal']))
            else:
                content.append(Paragraph(line, styles['Normal']))
            content.append(Spacer(1, 0.1*inch))

    # Build the PDF
    doc.build(content)

    return summary_path
