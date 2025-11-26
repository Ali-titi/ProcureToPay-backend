from rest_framework import serializers
from requests.models import PurchaseRequest, ReceiptValidation


class ReceiptValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptValidation
        fields = ['status', 'comment', 'date']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    description = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    department = serializers.CharField(read_only=True)
    proforma_file = serializers.FileField(read_only=True)
    receipt_validation = ReceiptValidationSerializer(read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'title', 'description', 'amount', 'quantity', 'department',
            'created_by_name', 'proforma_file', 'purchase_order_file',
            'receipt_file', 'status', 'created_at', 'updated_at', 'receipt_validation'
        ]
        read_only_fields = fields


class ReceiptValidationSerializer(serializers.Serializer):
    receipt_file = serializers.FileField()
    purchase_request_id = serializers.IntegerField()

    def validate_purchase_request_id(self, value):
        try:
            request = PurchaseRequest.objects.get(id=value, status='approved')
            return value
        except PurchaseRequest.DoesNotExist:
            raise serializers.ValidationError("Purchase request not found or not approved")