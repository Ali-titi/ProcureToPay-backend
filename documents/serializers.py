from rest_framework import serializers


class ProformaExtractionSerializer(serializers.Serializer):
    vendor_name = serializers.CharField(max_length=200)
    vendor_address = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class ReceiptValidationResultSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    discrepancies = serializers.ListField(
        child=serializers.DictField()
    )
    extracted_data = serializers.DictField()


class PurchaseOrderDataSerializer(serializers.Serializer):
    vendor_name = serializers.CharField()
    vendor_address = serializers.CharField(required=False)
    items = serializers.ListField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    request_id = serializers.IntegerField()
    created_by = serializers.CharField()