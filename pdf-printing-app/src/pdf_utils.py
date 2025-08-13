import requests
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)

def add_footer_text(pdf_stream, footer_text):
    reader = PdfReader(pdf_stream)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 5)
    can.drawString(100, 10, footer_text)
    can.save()

    packet.seek(0)
    footer_pdf = PdfReader(packet)
    footer_page = footer_pdf.pages[0]

    for i in range(len(writer.pages)):
        writer.pages[i].merge_page(footer_page)

    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

def save_modified_pdf(modified_pdf_stream, output_path):
    with open(output_path, 'wb') as output_file:
        output_file.write(modified_pdf_stream.read())