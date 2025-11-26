from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from requests.models import PurchaseRequest
from .serializers import ProformaExtractionSerializer, ReceiptValidationResultSerializer
from .services import extract, receipt_validation


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_proforma(request, request_id):
    try:
        purchase_request = PurchaseRequest.objects.get(id=request_id)
    except PurchaseRequest.DoesNotExist:
        return Response({'error': 'Purchase request not found'}, status=404)

    if not purchase_request.proforma_file:
        return Response({'error': 'No proforma file uploaded'}, status=400)

    # Extract data
    extracted_data = extract.extract_proforma_data(purchase_request.proforma_file.path)

    serializer = ProformaExtractionSerializer(data=extracted_data)
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_receipt(request, request_id):
    try:
        purchase_request = PurchaseRequest.objects.get(id=request_id, status='approved')
    except PurchaseRequest.DoesNotExist:
        return Response({'error': 'Purchase request not found or not approved'}, status=404)

    if not purchase_request.receipt_file:
        return Response({'error': 'No receipt file uploaded'}, status=400)

    # Validate receipt
    result = receipt_validation.validate_receipt(purchase_request.receipt_file.path, purchase_request)

    serializer = ReceiptValidationResultSerializer(data=result)
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=400)