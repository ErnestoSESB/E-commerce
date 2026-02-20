from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BaseProductViewSet, ProductVariationViewSet,
    UserViewSet, AddressViewSet,
    OrderViewSet, OrderItemViewSet,
    CartViewSet, CartItemViewSet,
    CRMTagViewSet, CustomerCRMViewSet, CRMInteractionViewSet,
    SupplierViewSet, InventoryLogViewSet, FinancialTransactionViewSet
)
router = DefaultRouter()

# Public and Mist
router.register(r'products', BaseProductViewSet, basename='product')
router.register(r'product-variations', ProductVariationViewSet, basename='product-variation')
router.register(r'users', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')

# Client
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')

# Staff/Admin
router.register(r'crm-tags', CRMTagViewSet, basename='crm-tag')
router.register(r'crm-customers', CustomerCRMViewSet, basename='crm-customer')
router.register(r'crm-interactions', CRMInteractionViewSet, basename='crm-interaction')

router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'inventory-logs', InventoryLogViewSet, basename='inventory-log')
router.register(r'financial-transactions', FinancialTransactionViewSet, basename='financial-transaction')

urlpatterns = [
    # Inclui as rotas da api como: /api/products/
    path('', include(router.urls)),
]
