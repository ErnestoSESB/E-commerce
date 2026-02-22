from rest_framework import serializers
from .utils import SanitizedCharField, RichTextField
from .models import (
    BaseProduct, ProductVariation, Address, BaseCustomUser, Order, 
    OrderItem, CartItem, Cart, CRMTag, CRMInteraction, CustomerCRM, 
    Supplier, InventoryLog, FinancialTransaction
)

class ProductSerializer(serializers.ModelSerializer):
    name = SanitizedCharField(max_length=125)
    description = RichTextField(required=False, allow_blank=True)
    class Meta:
        model = BaseProduct
        fields = ['id', 'name', 'price', 'description', 'slug', 'image']


class ProductDetailSerializer(serializers.ModelSerializer):
    name = SanitizedCharField(max_length=125)
    description = RichTextField(required=False, allow_blank=True)
    class Meta:
        model = BaseProduct
        fields = '__all__'


class SimpleProductSerializer(serializers.ModelSerializer):
    name = SanitizedCharField(max_length=125)
    class Meta:
        model = BaseProduct
        fields = ['id', 'name', 'price']
    def create(self, validated_data):
        validated_data['stock'] = 9999
        validated_data['description'] = "Produto Simples"
        validated_data['slug'] = validated_data['name'].lower().replace(" ", "-") 
        return super().create(validated_data)

class VariationProductSerializer(serializers.ModelSerializer):
    name = SanitizedCharField()
    value = SanitizedCharField()
    class Meta:
        model = ProductVariation
        fields = '__all__'

# Users
class AddressSerializer(serializers.ModelSerializer):
    street = SanitizedCharField()
    city = SanitizedCharField()
    state = SanitizedCharField()
    zip_code = SanitizedCharField()
    
    class Meta:
        model = Address
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
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
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField(source='get_total')
    class Meta:
        model = Order
        fields = ['id', 'client', 'status', 'payment_status', 'created_at', 'updated_at', 'items', 'total']

# Cart 
class CartItemSerializer(serializers.ModelSerializer):
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

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField() 
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total', 'user']

# CRM
class CRMTagSerializer(serializers.ModelSerializer):
    name = SanitizedCharField()
    color = SanitizedCharField()

    class Meta:
        model = CRMTag
        fields = '__all__'

class CRMInteractionSerializer(serializers.ModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent.username')
    subject = SanitizedCharField()
    description = SanitizedCharField()

    class Meta:
        model = CRMInteraction
        fields = '__all__'

class CustomerCRMSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.first_name')
    internal_notes = SanitizedCharField(required=False, allow_blank=True)
    tags = CRMTagSerializer(many=True, read_only=True)
    interactions = CRMInteractionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerCRM
        fields = '__all__'

# ERP
class SupplierSerializer(serializers.ModelSerializer):
    name = SanitizedCharField()
    contact_name = SanitizedCharField(allow_blank=True, required=False)
    notes = SanitizedCharField(allow_blank=True, required=False)
    class Meta:
        model = Supplier
        fields = '__all__'

class InventoryLogSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    user_name = serializers.ReadOnlyField(source='user.username')
    reason = SanitizedCharField()
    class Meta:
        model = InventoryLog
        fields = '__all__'

class FinancialTransactionSerializer(serializers.ModelSerializer):
    description = SanitizedCharField()
    category = SanitizedCharField(allow_blank=True, required=False)   
    class Meta:
        model = FinancialTransaction
        fields = '__all__'
