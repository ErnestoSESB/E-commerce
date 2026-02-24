from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from .utils import send_otp_email, send_password_reset_email
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter, OrderFilter, InventoryLogFilter, FinancialTransactionFilter, UserFilter
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
    SupplierSerializer, InventoryLogSerializer, FinancialTransactionSerializer,
    CustomTokenObtainPairSerializer
)
#AUTENTICAÇÃO DE DOIS FATORES

#verifica cria o token e verifica se o usuario tem
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  
        if response.status_code == 200:
            user = BaseCustomUser.objects.get(email=request.data.get('email'))
            if hasattr(user, 'security_profile') and user.security_profile.is_2fa_enabled:
                send_otp_email(user)
                return Response({
                    '2fa_required': True,
                    'email': user.email,
                    'message': 'Um código de verificação foi enviado para o seu email.'
                }, status=status.HTTP_200_OK)
        return response
    
#valida o codigo do token
class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        if not email or not otp_code:
            return Response({'error': 'Email e código OTP são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = BaseCustomUser.objects.get(email=email)
        except BaseCustomUser.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        profile = user.security_profile
        if not profile.otp_code or profile.otp_code != otp_code:
            return Response({'error': 'Código inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if profile.otp_created_at and timezone.now() > profile.otp_created_at + timedelta(minutes=10):
            return Response({'error': 'Código expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        profile.otp_code = None
        profile.otp_created_at = None
        profile.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

#recuperar senha
class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = BaseCustomUser.objects.get(email=email)
            send_password_reset_email(user)
        except BaseCustomUser.DoesNotExist:
            pass
        return Response({'message': 'Se o email existir em nossa base, um link de recuperação será enviado.'}, status=status.HTTP_200_OK)

#mudar senha
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not token or not new_password:
            return Response({'error': 'Token e nova senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = BaseCustomUser.objects.get(security_profile__reset_password_token=token)
        except BaseCustomUser.DoesNotExist:
            return Response({'error': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        profile = user.security_profile
        if profile.reset_password_expires and timezone.now() > profile.reset_password_expires:
            return Response({'error': 'Token expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        profile.reset_password_token = None
        profile.reset_password_expires = None
        profile.save()
        user.save()
        return Response({'message': 'Senha redefinida com sucesso.'}, status=status.HTTP_200_OK)

#permissões
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsStrictlyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Nega se não estiver autenticado e se não for Staff
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

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
    queryset = BaseProduct.objects.filter(is_active=True).order_by('created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['created_at']

class ProductVariationViewSet(viewsets.ModelViewSet):
    queryset = ProductVariation.objects.all()
    serializer_class = VariationProductSerializer
    permission_classes = [IsAdminOrReadOnly]

# Users
class UserViewSet(viewsets.ModelViewSet):
    queryset = BaseCustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['name', 'email']
    ordering_fields = ['date_joined', 'name']

    def get_permissions(self):
        if self.action == 'create': 
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['id', 'status']
    ordering_fields = ['created_at', 'status']
    ordering = ['created_at']

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

# CART
class CartViewSet(viewsets.ModelViewSet): 
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['created_at', 'id']
    ordering = ['created_at']

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

# ERP
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAdminUser]

class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = InventoryLogFilter
    ordering_fields = ['created_at', 'type']

class FinancialTransactionViewSet(viewsets.ModelViewSet):
    queryset = FinancialTransaction.objects.all().order_by('date')
    serializer_class = FinancialTransactionSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = FinancialTransactionFilter
    ordering_fields = ['date', 'amount']
    ordering = ['date']

