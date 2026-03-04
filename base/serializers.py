from rest_framework import serializers

class CleanModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        clean_representation = {}
        for key, value in representation.items():
            if value is not None and value != "" and value != 0 and value != [] and value != "0.00":
                clean_representation[key] = value
                
        return clean_representation

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import SanitizedCharField, RichTextField
from .models import (
    BaseProduct, ProductVariation, Address, BaseCustomUser, Order, 
    OrderItem, CartItem, Cart, CRMTag, CRMInteraction, CustomerCRM, 
    Supplier, InventoryLog, FinancialTransaction
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
class ProductSerializer(CleanModelSerializer):
    name = SanitizedCharField(max_length=125)
    description = RichTextField(required=False, allow_blank=True)
    class Meta:
        model = BaseProduct
        fields = ['id', 'name', 'price', 'description', 'slug', 'image']


class ProductDetailSerializer(CleanModelSerializer):
    name = SanitizedCharField(max_length=125)
    description = RichTextField(required=False, allow_blank=True)
    class Meta:
        model = BaseProduct
        fields = '__all__'


class SimpleProductSerializer(CleanModelSerializer):
    name = SanitizedCharField(max_length=125)
    class Meta:
        model = BaseProduct
        fields = ['id', 'name', 'price']
    def create(self, validated_data):
        validated_data['stock'] = 9999
        validated_data['description'] = "Produto Simples"
        validated_data['slug'] = validated_data['name'].lower().replace(" ", "-") 
        return super().create(validated_data)

class VariationProductSerializer(CleanModelSerializer):
    name = SanitizedCharField()
    value = SanitizedCharField()
    class Meta:
        model = ProductVariation
        fields = '__all__'

# Users
class AddressSerializer(CleanModelSerializer):
    street = SanitizedCharField()
    city = SanitizedCharField()
    state = SanitizedCharField()
    zip_code = SanitizedCharField()
    
    class Meta:
        model = Address
        fields = '__all__'

class CustomUserSerializer(CleanModelSerializer):
    address = AddressSerializer(read_only=True) 
    name = SanitizedCharField()
    
    class Meta:
        model = BaseCustomUser
        fields = ['username', 'email', 'name', 'phone', 'address', 'password']
        
        extra_kwargs = {
            'password': {'write_only': True}, 
            'username': {'read_only': True},  
            'email': {'read_only': True},     
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# Orders
class OrderItemSerializer(CleanModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity']

class OrderSerializer(CleanModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField(source='get_total')
    class Meta:
        model = Order
        fields = ['id', 'client', 'status', 'payment_status', 'created_at', 'updated_at', 'items', 'total']

# Cart 
class CartItemSerializer(CleanModelSerializer):
    id = serializers.UUIDField(read_only=True)
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity']
        read_only_fields = ['cart']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        
        if product and quantity:
            if product.stock is not None and quantity > product.stock:
                 raise serializers.ValidationError(f"Estoque insuficiente. Restam apenas {product.stock} unidades.")
        return data

class CartSerializer(CleanModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField() 
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total', 'user']

# CRM
class CRMTagSerializer(CleanModelSerializer):
    name = SanitizedCharField()
    color = SanitizedCharField()

    class Meta:
        model = CRMTag
        fields = '__all__'

class CRMInteractionSerializer(CleanModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent.username')
    subject = SanitizedCharField()
    description = SanitizedCharField()

    class Meta:
        model = CRMInteraction
        fields = '__all__'

class CustomerCRMSerializer(CleanModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.first_name')
    internal_notes = SanitizedCharField(required=False, allow_blank=True)
    tags = CRMTagSerializer(many=True, read_only=True)
    interactions = CRMInteractionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerCRM
        fields = '__all__'

# ERP
class SupplierSerializer(CleanModelSerializer):
    name = SanitizedCharField()
    contact_name = SanitizedCharField(allow_blank=True, required=False)
    notes = SanitizedCharField(allow_blank=True, required=False)
    class Meta:
        model = Supplier
        fields = '__all__'

class InventoryLogSerializer(CleanModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    user_name = serializers.ReadOnlyField(source='user.username')
    reason = SanitizedCharField()
    class Meta:
        model = InventoryLog
        fields = '__all__'

class FinancialTransactionSerializer(CleanModelSerializer):
    description = SanitizedCharField()
    category = SanitizedCharField(allow_blank=True, required=False)   
    class Meta:
        model = FinancialTransaction
        fields = '__all__'
