from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_l1', 'Pending L1'),
        ('rejected_l1', 'Rejected L1'),
        ('pending_l2', 'Pending L2'),
        ('rejected_l2', 'Rejected L2'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    department = models.CharField(max_length=100, blank=True, null=True)
    vendor_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    urgency = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_l1'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_requests'
    )
    proforma_file = models.FileField(
        upload_to='proformas/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.status}"

    def can_edit(self):
        """Check if request can be edited (only pending_l1 status)"""
        return self.status == 'pending_l1'

    def can_approve(self, user):
        """Check if user can approve this request"""
        if user.role == 'approver1' and self.status == 'pending_l1':
            return True
        elif user.role == 'approver2' and self.status == 'pending_l2':
            return True
        return False

    def approve(self, user, comment=''):
        """Approve the request"""
        with transaction.atomic():
            level = 1 if user.role == 'approver1' else 2
            Approval.objects.create(
                purchase_request=self,
                approver=user,
                level=level,
                status='approved',
                comment=comment
            )

            if level == 1:
                self.status = 'pending_l2'
            elif level == 2:
                self.status = 'approved'
            self.save()

    def reject(self, user, comment=''):
        """Reject the request"""
        with transaction.atomic():
            level = 1 if user.role == 'approver1' else 2
            Approval.objects.create(
                purchase_request=self,
                approver=user,
                level=level,
                status='rejected',
                comment=comment
            )
            if level == 1:
                self.status = 'rejected_l1'
            elif level == 2:
                self.status = 'rejected_l2'
            self.save()


class Approval(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    level = models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['purchase_request', 'level']
        ordering = ['date']

    def __str__(self):
        return f"{self.purchase_request.title} - Level {self.level} - {self.status}"


class Attachment(models.Model):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.purchase_request.title}"


class ReceiptValidation(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('partially_received', 'Partially Received'),
        ('not_received', 'Not Received'),
    ]

    purchase_request = models.OneToOneField(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='receipt_validation'
    )
    finance_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Validation for {self.purchase_request.title} - {self.status}"


class RequestItem(models.Model):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.item_name} - {self.quantity} x {self.price}"