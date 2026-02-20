from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    BaseProduct, ProductVariation, BaseCustomUser, Address,
    Order, OrderItem, Cart, CartItem, CRMTag, CustomerCRM,
    CRMInteraction, Supplier, InventoryLog, FinancialTransaction
)
from .serializers import (
    ProductSerializer, VariationProductSerializer,
    CustomUserSerializer, AddressSerializer,
    OrderSerializer, OrderItemSerializer,
    CartSerializer, CartItemSerializer,
    CRMTagSerializer, CustomerCRMSerializer, CRMInteractionSerializer,
    SupplierSerializer, InventoryLogSerializer, FinancialTransactionSerializer
)
#permissões
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if hasattr(obj, 'client'):
            return obj.client == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user

# Products
class BaseProductViewSet(viewsets.ModelViewSet):
    queryset = BaseProduct.objects.filter(is_active=True) 
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class ProductVariationViewSet(viewsets.ModelViewSet):
    queryset = ProductVariation.objects.all()
    serializer_class = VariationProductSerializer
    permission_classes = [IsAdminOrReadOnly]

# Users
class UserViewSet(viewsets.ModelViewSet):
    queryset = BaseCustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create': 
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated, IsOwnerOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return BaseCustomUser.objects.all()
        return BaseCustomUser.objects.filter(id=user.id)

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Address.objects.all()
        return Address.objects.filter(basecustomuser=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.address:
            user.address.delete()
        address_instance = serializer.save()
        user.address = address_instance
        user.save()



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- CARRINHO ---
class CartViewSet(viewsets.ModelViewSet): 
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Cart.objects.all()
        cart, created = Cart.objects.get_or_create(user=user)
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CartItem.objects.all()
        return CartItem.objects.filter(cart__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        serializer.save(cart=cart)

#CRM
class CRMTagViewSet(viewsets.ModelViewSet):
    queryset = CRMTag.objects.all()
    serializer_class = CRMTagSerializer
    permission_classes = [permissions.IsAdminUser] 

class CustomerCRMViewSet(viewsets.ModelViewSet):
    queryset = CustomerCRM.objects.all()
    serializer_class = CustomerCRMSerializer
    permission_classes = [permissions.IsAdminUser] 

class CRMInteractionViewSet(viewsets.ModelViewSet):
    queryset = CRMInteraction.objects.all()
    serializer_class = CRMInteractionSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(agent=self.request.user)

# --- ERP (APENAS ADMIN/STAFF) ---
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]

class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer
    permission_classes = [permissions.IsAdminUser]

class FinancialTransactionViewSet(viewsets.ModelViewSet):
    queryset = FinancialTransaction.objects.all()
    serializer_class = FinancialTransactionSerializer
    permission_classes = [permissions.IsAdminUser]

