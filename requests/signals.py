from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseRequest
from documents.services import po_generator


# @receiver(post_save, sender=PurchaseRequest)
# def generate_purchase_order(sender, instance, created, **kwargs):
#     """Generate PO when request is approved"""
#     if instance.status == 'approved' and not instance.purchase_order_file:
#         # Generate PO
#         po_file = po_generator.generate_po(instance)
#         if po_file:
#             instance.purchase_order_file = po_file
#             instance.save(update_fields=['purchase_order_file'])