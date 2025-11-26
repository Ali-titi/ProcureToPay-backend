from django.urls import path
from . import views

urlpatterns = [
    path('requests/<int:request_id>/extract-proforma/', views.extract_proforma, name='extract_proforma'),
    path('requests/<int:request_id>/validate-receipt/', views.validate_receipt, name='validate_receipt'),
]