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
        print(f"Response length: {len(response.content)} bytes")
        
        if 'Content-Disposition' in response.headers:
            print("Found Content-Disposition header - direct download successful")
            content = response.content
        else:
            print("No Content-Disposition header, attempting alternative methods...")
            
            # Try different approaches to get the download token
            download_token = None
            
            # Method 1: Look for the standard confirm token
            if 'confirm=' in response.text:
                token_start = response.text.find('confirm=') + 8
                token_end = response.text.find('&', token_start)
                if token_end == -1:
                    token_end = response.text.find('"', token_start)
                if token_end != -1:
                    download_token = response.text[token_start:token_end]
                    print(f"Found standard download token: {download_token}")
            
            # Method 2: Try with a simple 't' token
            if not download_token:
                print("Trying with simple token 't'...")
                download_token = 't'
            
            # Make the actual download request with the token
            params['confirm'] = download_token
            
            # Remove any existing cookies and use a fresh session
            session = requests.Session()
            
            # Add specific headers for file download
            download_headers = headers.copy()
            download_headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            print(f"Making download request with token: {download_token}")
            response = session.get(url, params=params, headers=download_headers, cookies=cookies, allow_redirects=True)
            response.raise_for_status()
            
            print(f"Download response status: {response.status_code}")
            print(f"Download response headers: {dict(response.headers)}")
            
            if 'Content-Type' in response.headers:
                print(f"Download Content-Type: {response.headers['Content-Type']}")
            
            content = response.content
            print(f"Downloaded content size: {len(content)} bytes")
        
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
        # Try the direct usercontent.google.com URL first
        direct_url = f'https://drive.usercontent.google.com/download?id={file_id}&export=download'
        print(f"Trying direct usercontent URL: {direct_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
        }
        
        try:
            # First attempt with the direct URL
            session = requests.Session()
            response = session.get(direct_url, headers=headers)
            if response.status_code == 200 and response.headers.get('Content-Type', '').startswith(('application/pdf', 'application/octet-stream')):
                print("Direct URL successful!")
                return io.BytesIO(response.content)
        except Exception as e:
            print(f"Direct URL attempt failed: {str(e)}")
        
        # If direct URL fails, try the traditional method
        cookies = {
            'download_warning_13058876_1': '1',
        }
        
        params = {
            'id': file_id,
            'export': 'download',
            'confirm': 't',
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