from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseProduct
        fields = '__all__'


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseProduct
        fields = ['id', 'name', 'price']
        
    def create(self, validated_data):
        validated_data['stock'] = 9999
        validated_data['description'] = "Produto Simples"
        validated_data['slug'] = validated_data['name'].lower().replace(" ", "-") 
        return super().create(validated_data)

class VariationProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = '__all__'

# Users
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True) 
    class Meta:
        model = BaseCustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True},
            'groups': {'read_only': True},
            'user_permissions': {'read_only': True},
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

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField() 

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total']

# CRM
class CRMTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMTag
        fields = '__all__'

class CRMInteractionSerializer(serializers.ModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent.username')

    class Meta:
        model = CRMInteraction
        fields = '__all__'

class CustomerCRMSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.ReadOnlyField(source='user.first_name')
    tags = CRMTagSerializer(many=True, read_only=True)
    interactions = CRMInteractionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerCRM
        fields = '__all__'

# ERP
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class InventoryLogSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = InventoryLog
        fields = '__all__'

class FinancialTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialTransaction
        fields = '__all__'
