import requests
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def download_pdf(url):
    print(f"Starting download from URL: {url}")
    
    # Extract file ID from Google Drive URL if present
    file_id = None
    if 'drive.google.com' in url or 'drive.usercontent.google.com' in url:
        if 'id=' in url:
            file_id = url.split('id=')[1].split('&')[0]
        elif '/d/' in url:
            file_id = url.split('/d/')[1].split('/')[0]
        
        print(f"Extracted Google Drive file ID: {file_id}")
    
    if file_id:
        # Use the direct download URL format
        url = f'https://drive.google.com/uc?export=download&id={file_id}'
        print(f"Using Google Drive direct download URL: {url}")
    
    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,application/octet-stream',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    try:
        print("Making initial request...")
        # Make initial request with cookies enabled
        session = requests.Session()
        response = session.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        print(f"Initial response status code: {response.status_code}")
        print(f"Initial response headers: {dict(response.headers)}")
        
        # Check if we got a Google Drive "virus scan" warning page
        if 'Content-Type' in response.headers and 'text/html' in response.headers['Content-Type'].lower():
            print("Received HTML response, checking for virus scan warning...")
            
            # Get the confirmation token
            if 'Google Drive - Virus scan warning' in response.text:
                print("Detected virus scan warning page, attempting to bypass...")
                confirm_url = f'https://drive.google.com/uc?export=download&confirm=t&id={file_id}'
                print(f"Using confirmation URL: {confirm_url}")
                
                response = session.get(confirm_url, headers=headers, stream=True)
                response.raise_for_status()
                print(f"Confirmation response status code: {response.status_code}")
                print(f"Confirmation response headers: {dict(response.headers)}")
        
        # Verify content type is PDF or binary
        content_type = response.headers.get('Content-Type', '').lower()
        print(f"Final response content type: {content_type}")
        
        if not ('pdf' in content_type or 'octet-stream' in content_type or 'application/x-download' in content_type):
            if len(response.content) < 1000:  # If response is small, it might be an error page
                print(f"Response content (first 1000 bytes): {response.content[:1000]}")
            raise Exception(f"Unexpected content type: {content_type}")
            
        content = response.content
        print(f"Downloaded content size: {len(content)} bytes")
        
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