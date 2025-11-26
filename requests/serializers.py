from rest_framework import serializers
from .models import PurchaseRequest, Approval, RequestItem, Attachment, ReceiptValidation


class RequestItemSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()

    class Meta:
        model = RequestItem
        fields = ['id', 'item_name', 'price', 'quantity', 'total']


class ApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    approver_role = serializers.CharField(source='approver.role', read_only=True)

    class Meta:
        model = Approval
        fields = ['id', 'approver', 'approver_name', 'approver_role', 'level', 'status', 'comment', 'date']
        read_only_fields = ['id', 'date']


class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = RequestItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            'id', 'title', 'description', 'amount', 'quantity', 'department', 'vendor_name', 'category', 'urgency', 'status',
            'created_by', 'created_by_name',
            'proforma_file',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'created_by', 'created_by_name', 'items']


class PurchaseRequestDetailSerializer(PurchaseRequestSerializer):
    approvals = ApprovalSerializer(many=True, read_only=True)

    class Meta(PurchaseRequestSerializer.Meta):
        fields = PurchaseRequestSerializer.Meta.fields + ['approvals']


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    items = RequestItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseRequest
        fields = ['title', 'description', 'amount', 'quantity', 'department', 'vendor_name', 'category', 'urgency', 'proforma_file', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        validated_data['created_by'] = self.context['request'].user
        request = PurchaseRequest.objects.create(**validated_data)

        for item_data in items_data:
            RequestItem.objects.create(purchase_request=request, **item_data)

        return request


class ApprovalActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ReceiptValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptValidation
        fields = ['status', 'comment']