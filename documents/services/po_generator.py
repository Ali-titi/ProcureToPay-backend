from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from requests.models import PurchaseRequest


def generate_po(purchase_request):
    """Generate a Purchase Order PDF from approved request"""
    if not isinstance(purchase_request, PurchaseRequest):
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("PURCHASE ORDER", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # PO Details
    po_data = [
        ['PO Number:', f'PO-{purchase_request.id:04d}'],
        ['Date:', purchase_request.created_at.strftime('%Y-%m-%d')],
        ['Vendor:', 'Extracted from Proforma'],  # TODO: Use extracted vendor
        ['Requested By:', purchase_request.created_by.get_full_name()],
        ['Amount:', f'${purchase_request.amount}'],
    ]

    po_table = Table(po_data, colWidths=[100, 300])
    po_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(po_table)
    story.append(Spacer(1, 20))

    # Items
    if purchase_request.items.exists():
        items_data = [['Item', 'Quantity', 'Price', 'Total']]
        for item in purchase_request.items.all():
            items_data.append([
                item.item_name,
                str(item.quantity),
                f'${item.price}',
                f'${item.total}'
            ])

        items_table = Table(items_data, colWidths=[200, 80, 80, 80])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(items_table)

    doc.build(story)

    # Save to file
    buffer.seek(0)
    file_name = f'po_{purchase_request.id}.pdf'
    file_path = f'purchase_orders/{file_name}'

    # Save file
    file_content = ContentFile(buffer.getvalue())
    saved_path = default_storage.save(file_path, file_content)

    return saved_path