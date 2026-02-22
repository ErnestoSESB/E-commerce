import django_filters
from django.core.exceptions import PermissionDenied
from .models import BaseProduct, Order, InventoryLog, FinancialTransaction, BaseCustomUser

class BasePermissionFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_permissions()

    def check_permissions(self):
        pass

    @property
    def user(self):
        return self.request.user if self.request else None

class ProductFilter(BasePermissionFilter):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = BaseProduct
        fields = ['is_active', 'min_price', 'max_price', 'name']
    
    def check_permissions(self):
        if self.data.get('is_active') is not None:
             if not (self.user and self.user.is_staff):
                 raise PermissionDenied("Apenas administradores podem filtrar por status de atividade.")

class OrderFilter(BasePermissionFilter):
    min_date = django_filters.DateFilter(field_name="created_at", lookup_expr='gte')
    max_date = django_filters.DateFilter(field_name="created_at", lookup_expr='lte')
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')

    class Meta:
        model = Order
        fields = ['status', 'min_date', 'max_date', 'client']

    def check_permissions(self):
        if self.data.get('client'):
             if not (self.user and self.user.is_staff):
                 raise PermissionDenied("Acesso negado: Você não tem permissão para filtrar pedidos de outros clientes.")

class InventoryLogFilter(BasePermissionFilter):
    min_date = django_filters.DateFilter(field_name="created_at", lookup_expr='gte')
    max_date = django_filters.DateFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = InventoryLog
        fields = ['product', 'type', 'min_date', 'max_date']
    
    def check_permissions(self):
        if not (self.user and self.user.is_staff):
            raise PermissionDenied("Acesso restrito: Logs de inventário são exclusivos para administradores.")

class UserFilter(BasePermissionFilter):
    id = django_filters.UUIDFilter(field_name="id")
    email = django_filters.CharFilter(field_name="email", lookup_expr='exact')
    phone = django_filters.CharFilter(field_name="phone", lookup_expr='exact')
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    is_staff = django_filters.BooleanFilter(field_name="is_staff")
    user_type = django_filters.CharFilter(field_name="user_type", lookup_expr='exact')

    class Meta:
        model = BaseCustomUser
        fields = ['id', 'email', 'phone', 'name', 'is_staff', 'user_type']

    def check_permissions(self):
        sensitive_fields = ['id', 'email', 'phone', 'is_staff', 'user_type']
        is_filtering_sensitive = any(self.data.get(field) for field in sensitive_fields)
        if is_filtering_sensitive:
            if not (self.user and self.user.is_staff):
                 raise PermissionDenied(f"Acesso negado: Apenas administradores e staffs podem filtrar por dados sensíveis como {', '.join(sensitive_fields)}.")

class FinancialTransactionFilter(BasePermissionFilter):
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='lte')
    min_date = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    max_date = django_filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = FinancialTransaction
        fields = ['type', 'min_amount', 'max_amount', 'min_date', 'max_date']

    def check_permissions(self):
        if not (self.user and self.user.is_staff):
            raise PermissionDenied("PERIGO: Tentativa de acesso não autorizado a dados financeiros.")