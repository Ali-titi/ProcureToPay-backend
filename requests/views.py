from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import PurchaseRequest, Attachment, ReceiptValidation
from .serializers import (
    PurchaseRequestSerializer, PurchaseRequestDetailSerializer,
    PurchaseRequestCreateSerializer, ApprovalActionSerializer,
    FileUploadSerializer, AttachmentSerializer, ReceiptValidationSerializer
)
from .permissions import IsStaff, IsApprover, IsOwnerOrReadOnly, CanApproveRequest
from finance.permissions import IsFinanceUser
from documents.services import extract


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseRequestCreateSerializer
        elif self.action == 'retrieve':
            return PurchaseRequestDetailSerializer
        return PurchaseRequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsStaff()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsStaff()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'staff':
            return PurchaseRequest.objects.filter(created_by=user)
        elif user.role == 'approver1':
            return PurchaseRequest.objects.filter(status='pending_l1')
        elif user.role == 'approver2':
            return PurchaseRequest.objects.filter(status='pending_l2')
        elif user.role == 'finance':
            return PurchaseRequest.objects.filter(status='approved')
        elif user.role == 'admin':
            return PurchaseRequest.objects.all()
        return PurchaseRequest.objects.none()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_approvals(self, request):
        """Get all requests that the current user has approved"""
        user = request.user
        if user.role not in ['approver1', 'approver2', 'admin']:
            return Response({'error': 'Access denied'}, status=403)

        requests = PurchaseRequest.objects.filter(
            approvals__approver=user
        ).distinct()

        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsStaff])
    def upload_proforma(self, request, pk=None):
        obj = self.get_object()
        if obj.status != 'pending':
            return Response({'error': 'Cannot upload to non-pending request'}, status=400)

        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            obj.proforma_file = serializer.validated_data['file']
            obj.save()

            # Extract data from proforma
            extracted_data = extract.extract_proforma_data(obj.proforma_file.path)
            # TODO: Store extracted data

            return Response({'message': 'Proforma uploaded successfully'})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsFinanceUser])
    def upload_receipt(self, request, pk=None):
        obj = self.get_object()
        if obj.status != 'approved':
            return Response({'error': 'Cannot upload receipt to non-approved request'}, status=400)

        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            obj.receipt_file = serializer.validated_data['file']
            obj.save()
            return Response({'message': 'Receipt uploaded successfully'})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveRequest])
    def approve(self, request, pk=None):
        obj = self.get_object()
        serializer = ApprovalActionSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.validated_data.get('comment', '')
            obj.approve(request.user, comment)
            return Response({'message': 'Request approved'})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveRequest])
    def reject(self, request, pk=None):
        obj = self.get_object()
        serializer = ApprovalActionSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.validated_data.get('comment', '')
            obj.reject(request.user, comment)
            return Response({'message': 'Request rejected'})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_attachment(self, request, pk=None):
        obj = self.get_object()
        # Allow staff to upload to their own pending requests, approvers to any, etc.
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            Attachment.objects.create(
                purchase_request=obj,
                file=serializer.validated_data['file']
            )
            return Response({'message': 'Attachment uploaded successfully'})
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def attachments(self, request, pk=None):
        obj = self.get_object()
        attachments = obj.attachments.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsApprover])
def pending_approvals(request):
    user = request.user
    if user.role == 'approver1':
        requests = PurchaseRequest.objects.filter(status='pending_l1')
    elif user.role == 'approver2':
        requests = PurchaseRequest.objects.filter(status='pending_l2')
    else:
        requests = PurchaseRequest.objects.none()

    serializer = PurchaseRequestSerializer(requests, many=True)
    return Response(serializer.data)