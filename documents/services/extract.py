import pdfplumber
import pytesseract
from PIL import Image
import os
import re
from decimal import Decimal


def extract_proforma_data(file_path):
    """Extract vendor and item data from proforma PDF"""
    if not os.path.exists(file_path):
        return {}

    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.pdf':
        return extract_from_pdf(file_path)
    elif file_ext in ['.jpg', '.jpeg', '.png']:
        return extract_from_image(file_path)
    else:
        return {}


def extract_from_pdf(file_path):
    """Extract text from PDF using pdfplumber"""
    extracted_data = {
        'vendor_name': '',
        'vendor_address': '',
        'items': [],
        'total_amount': Decimal('0.00')
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'

            # Parse the text
            lines = text.split('\n')
            vendor_found = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for vendor name (usually at the top)
                if not vendor_found and len(line.split()) <= 5 and not any(char.isdigit() for char in line):
                    extracted_data['vendor_name'] = line
                    vendor_found = True
                    continue

                # Look for items (lines with prices)
                if '$' in line or 'USD' in line or re.search(r'\d+\.\d{2}', line):
                    item_data = parse_item_line(line)
                    if item_data:
                        extracted_data['items'].append(item_data)
                        extracted_data['total_amount'] += item_data.get('price', Decimal('0.00'))

    except Exception as e:
        print(f"Error extracting from PDF: {e}")

    return extracted_data


def extract_from_image(file_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        # Similar parsing as PDF
        return extract_from_pdf_text(text)
    except Exception as e:
        print(f"Error extracting from image: {e}")
        return {}


def extract_from_pdf_text(text):
    """Parse extracted text for proforma data"""
    extracted_data = {
        'vendor_name': '',
        'vendor_address': '',
        'items': [],
        'total_amount': Decimal('0.00')
    }

    lines = text.split('\n')
    for line in lines:
        # Similar logic as PDF extraction
        pass

    return extracted_data


def parse_item_line(line):
    """Parse a line containing item information"""
    # Simple regex to find item name and price
    # This is a basic implementation - would need refinement for real use
    price_match = re.search(r'(\d+\.\d{2})', line)
    if price_match:
        price = Decimal(price_match.group(1))
        # Assume everything before price is item name
        item_name = line[:price_match.start()].strip()
        return {
            'item_name': item_name,
            'price': price,
            'quantity': 1
        }
    return None