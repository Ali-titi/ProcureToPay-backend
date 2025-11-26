from django.contrib import admin
from .models import PurchaseRequest, Approval, RequestItem, Attachment, ReceiptValidation


class RequestItemInline(admin.TabularInline):
    model = RequestItem
    extra = 0


class ApprovalInline(admin.TabularInline):
    model = Approval
    extra = 0
    readonly_fields = ('date',)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'amount', 'quantity', 'department', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at', 'department')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RequestItemInline, ApprovalInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'amount', 'quantity', 'department', 'status')
        }),
        ('Users', {
            'fields': ('created_by',)
        }),
        ('Files', {
            'fields': ('proforma_file', 'receipt_file', 'purchase_order_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'approver', 'level', 'status', 'date')
    list_filter = ('level', 'status', 'date')
    search_fields = ('purchase_request__title', 'approver__username')
    readonly_fields = ('date',)


@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'item_name', 'price', 'quantity', 'total')
    list_filter = ('purchase_request__status',)
    search_fields = ('item_name', 'purchase_request__title')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('purchase_request__title',)


@admin.register(ReceiptValidation)
class ReceiptValidationAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'finance_user', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('purchase_request__title', 'finance_user__username')
    readonly_fields = ('date',)