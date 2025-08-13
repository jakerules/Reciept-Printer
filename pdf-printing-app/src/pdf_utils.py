import requests
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def download_pdf(url):
    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        # Make initial request
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        response.raise_for_status()
        
        # Check if we got a Google Drive "virus scan" warning page
        if 'Content-Type' in response.headers and 'text/html' in response.headers['Content-Type'].lower():
            # Extract the download link from the response if it's the virus scan page
            if 'Google Drive - Virus scan warning' in response.text:
                confirm_url = url + '&confirm=t'
                response = requests.get(confirm_url, headers=headers, stream=True)
                response.raise_for_status()
        
        content = response.content
        
        # Verify it's a valid PDF
        pdf_stream = io.BytesIO(content)
        try:
            # Try to read the PDF to validate it
            PdfReader(pdf_stream)
            pdf_stream.seek(0)  # Reset stream position
            return pdf_stream
        except Exception as e:
            raise Exception(f"Invalid or corrupted PDF file: {str(e)}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download PDF: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

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

# Test code - add this temporarily to test the download
if __name__ == "__main__":
    url = "https://drive.usercontent.google.com/download?id=1uvxBexf1DkgejM8hEfpsijW9aM9fhJFt&export=download&authuser=0"
    try:
        pdf_stream = download_pdf(url)
        print("PDF downloaded successfully!")
        # Save to a test file to verify content
        with open("test_download.pdf", "wb") as f:
            f.write(pdf_stream.getvalue())
    except Exception as e:
        print(f"Error: {e}")