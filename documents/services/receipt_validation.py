import pdfplumber
import pytesseract
from PIL import Image
import os
import re
from decimal import Decimal


def validate_receipt(receipt_file, purchase_request):
    """Validate receipt against purchase order"""
    if hasattr(receipt_file, 'path'):
        file_path = receipt_file.path
    else:
        file_path = receipt_file

    if not os.path.exists(file_path):
        return {
            'is_valid': False,
            'discrepancies': ['Receipt file not found'],
            'extracted_data': {}
        }

    # Extract data from receipt
    extracted_data = extract_receipt_data(file_path)

    # Compare with PO
    discrepancies = []
    is_valid = True

    # Check total amount
    if extracted_data.get('total_amount'):
        po_amount = purchase_request.amount
        receipt_amount = extracted_data['total_amount']

        if abs(po_amount - receipt_amount) > Decimal('0.01'):  # Allow 1 cent difference
            discrepancies.append(f'Amount mismatch: PO ${po_amount}, Receipt ${receipt_amount}')
            is_valid = False

    # Check vendor (if available)
    # TODO: Compare vendor names

    # Check items (if available)
    if extracted_data.get('items') and purchase_request.items.exists():
        po_items = {item.item_name.lower(): item.total for item in purchase_request.items.all()}
        receipt_items = {item['name'].lower(): item['price'] for item in extracted_data['items']}

        for item_name, po_price in po_items.items():
            if item_name not in receipt_items:
                discrepancies.append(f'Item "{item_name}" not found in receipt')
                is_valid = False
            elif abs(po_price - receipt_items[item_name]) > Decimal('0.01'):
                discrepancies.append(f'Price mismatch for "{item_name}": PO ${po_price}, Receipt ${receipt_items[item_name]}')
                is_valid = False

    return {
        'is_valid': is_valid,
        'discrepancies': discrepancies,
        'extracted_data': extracted_data
    }


def extract_receipt_data(file_path):
    """Extract data from receipt"""
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.pdf':
        return extract_receipt_from_pdf(file_path)
    elif file_ext in ['.jpg', '.jpeg', '.png']:
        return extract_receipt_from_image(file_path)
    else:
        return {}


def extract_receipt_from_pdf(file_path):
    """Extract receipt data from PDF"""
    extracted_data = {
        'vendor_name': '',
        'items': [],
        'total_amount': Decimal('0.00')
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'

            # Parse receipt text
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Look for total
                if 'total' in line.lower():
                    amount_match = re.search(r'(\d+\.\d{2})', line)
                    if amount_match:
                        extracted_data['total_amount'] = Decimal(amount_match.group(1))

                # Look for items
                elif re.search(r'\d+\.\d{2}', line) and len(line.split()) > 2:
                    item_data = parse_receipt_item_line(line)
                    if item_data:
                        extracted_data['items'].append(item_data)

    except Exception as e:
        print(f"Error extracting receipt from PDF: {e}")

    return extracted_data


def extract_receipt_from_image(file_path):
    """Extract receipt data from image"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        # Similar parsing logic
        return extract_receipt_from_pdf_text(text)
    except Exception as e:
        print(f"Error extracting receipt from image: {e}")
        return {}


def extract_receipt_from_pdf_text(text):
    """Parse receipt text"""
    extracted_data = {
        'vendor_name': '',
        'items': [],
        'total_amount': Decimal('0.00')
    }

    lines = text.split('\n')
    for line in lines:
        # Similar logic as PDF
        pass

    return extracted_data


def parse_receipt_item_line(line):
    """Parse receipt item line"""
    price_match = re.search(r'(\d+\.\d{2})', line)
    if price_match:
        price = Decimal(price_match.group(1))
        name = line[:price_match.start()].strip()
        return {
            'name': name,
            'price': price
        }
    return None