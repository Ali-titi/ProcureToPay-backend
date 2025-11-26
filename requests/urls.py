from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'requests', views.PurchaseRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('approvals/pending/', views.pending_approvals, name='pending_approvals'),
]