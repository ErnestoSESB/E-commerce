from django.contrib import admin
from .models import (
    BaseProduct, ProductVariation, 
    BaseCustomUser, Address,
    Order, OrderItem,
    Cart, CartItem,
    CRMTag, CustomerCRM, CRMInteraction,
    Supplier, InventoryLog, FinancialTransaction
)


admin.site.site_header = "Administração Nexum"
admin.site.site_title = "Painel Gerencial"
admin.site.index_title = "Bem-vindo ao Gerenciamento do E-commerce"


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

@admin.register(BaseProduct)
class BaseProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    inlines = [ProductVariationInline]
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price_display', 'quantity')

    def has_add_permission(self, request, obj=None):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

    def price_display(self, obj):
        return obj.product.price if obj.product else '-'
    price_display.short_description = 'Preço Unitário'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total_pedido', 'status', 'payment_status', 'created_at')
    search_fields = ('id', 'client__email', 'client__name')
    list_filter = ('status', 'payment_status', 'created_at')
    inlines = [OrderItemInline]

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ('client', 'created_at', 'updated_at')
        return ('created_at', 'updated_at')


    def has_delete_permission(self, request, obj=None):
        return False

    def total_pedido(self, obj):
        return f"R$ {obj.get_total:.2f}"
    total_pedido.short_description = 'Total'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__email', 'id')
    inlines = [CartItemInline]


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0

@admin.register(BaseCustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'user_type', 'is_active', 'created_at')
    search_fields = ('email', 'name', 'phone')
    list_filter = ('user_type', 'is_active', 'is_staff')


class CRMInteractionInline(admin.TabularInline):
    model = CRMInteraction
    extra = 1

@admin.register(CustomerCRM)
class CustomerCRMAdmin(admin.ModelAdmin):
    list_display = ('user', 'lifetime_value', 'total_orders_count', 'last_purchase_date')
    search_fields = ('user__email', 'user__name')
    filter_horizontal = ('tags',)
    inlines = [CRMInteractionInline]
    readonly_fields = ('lifetime_value', 'total_orders_count', 'last_purchase_date')

@admin.register(CRMTag)
class CRMTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone', 'email')
    search_fields = ('name', 'contact_name', 'email')

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation', 'type', 'quantity', 'user', 'created_at')
    search_fields = ('product__name', 'reason', 'user__email')
    list_filter = ('type', 'created_at')
    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return [f.name for f in self.model._meta.fields]
        return ('created_at',)

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'amount', 'date')
    search_fields = ('description', 'id')
    list_filter = ('type', 'date')


    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return [f.name for f in self.model._meta.fields] 
        return []

    def has_delete_permission(self, request, obj=None):
        return False

