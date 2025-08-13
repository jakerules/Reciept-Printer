import requests
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def _download_google_drive(url, params, headers, cookies):
    """Helper function to handle Google Drive downloads with proper authentication."""
    print("Attempting Google Drive download...")
    session = requests.Session()
    
    try:
        # First request to get the download token
        response = session.get(url, params=params, headers=headers, cookies=cookies)
        response.raise_for_status()
        
        print(f"Initial response status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        if 'Content-Disposition' in response.headers:
            print("Found Content-Disposition header - direct download successful")
            content = response.content
        else:
            # If we got HTML, look for the download form
            print("Looking for download token in response...")
            download_token = None
            
            if 'confirm=' in response.text:
                token_start = response.text.find('confirm=') + 8
                token_end = response.text.find('&', token_start)
                if token_end == -1:
                    token_end = response.text.find('"', token_start)
                download_token = response.text[token_start:token_end]
                
                print(f"Found download token: {download_token}")
                
                # Make the actual download request
                params['confirm'] = download_token
                response = session.get(url, params=params, headers=headers, cookies=cookies)
                response.raise_for_status()
                content = response.content
            else:
                raise Exception("Could not find download token in response")
        
        # Verify the content is a PDF
        if content.startswith(b'%PDF-'):
            print("Content verified as PDF")
            return io.BytesIO(content)
        else:
            raise Exception("Downloaded content is not a PDF file")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download from Google Drive: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing Google Drive download: {str(e)}")

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
        
        # For Google Drive, we'll use a different approach
        cookies = {
            'download_warning_13058876_1': '1',
            'NID': '511=GHpX3L9h-Zk9ovH9plzL_RaUPFYQgnkp4YAOXgL13w',
        }
        
        headers = {
            'Authority': 'drive.google.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'X-Chrome-Connected': 'source=Chrome,id=115.0.0.0,mode=0,enable_account_consistency=1,consistency_enable_account_manager=1',
        }
        
        params = {
            'id': file_id,
            'export': 'download',
            'confirm': 't',
            'uuid': '869c3f61-76f1-4592-87cf-756a87d19e22',
            'at': 'AHAOulvmEmKF_kauHCXKwxcGBXmY:1692159556590',
        }
        
        url = 'https://drive.google.com/uc'
        return _download_google_drive(url, params, headers, cookies)
    
    # For non-Google Drive URLs, use standard headers
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