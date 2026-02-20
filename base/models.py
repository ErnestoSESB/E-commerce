from django.db import models

#DOCUMENTATION ABOUT ID'S
import uuid

#DOCUMENTATION ABOUT USER'S
from django.contrib.auth.models import AbstractUser
#aponta para o modelo correto de usuario
from django.conf import settings

#PRODUCTS

class BaseProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True) 
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        
        if not self.slug and self.name:
             
             from django.utils.text import slugify
             base_slug = slugify(self.name)
             self.slug = f"{base_slug}-{str(self.id)[:8]}" if self.id else base_slug
        super().save(*args, **kwargs)
 
#caso haja variação do produto - usar aqui

class ProductVariation(models.Model):
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE, related_name='variations')
    name = models.CharField(max_length=50) 
    value = models.CharField(max_length=50) 
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

#USERS

class Address(models.Model):
    street = models.CharField(max_length=255)
    number = models.PositiveIntegerField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

class BaseCustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Cliente'), #ver
        ('manager', 'Gerente'), # ver e ver vendas
        ('employee', 'Funcionário'), #ver pedidos, e mudar status
        ('admin', 'Administrador'), # All
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='client')
    
    name = models.CharField(max_length=125)
    phone = models.PhoneNumberField(blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    def is_manager_or_admin(self):
        return self.user_type in ['manager', 'admin'] or self.is_superuser
    
    def save(self, *args, **kwargs):

        if self.user_type in ['manager', 'employee', 'admin']:
            self.is_staff = True
        if self.user_type == 'admin':
            self.is_superuser = True
        super().save(*args, **kwargs)


# ORDERS 

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    @property
    def get_total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    @property
    def get_products_and_quantities(self): 
        #retorna tuplas em lista
        return [(item.product, item.quantity) for item in self.items.all()]

    STATUS_CHOICE = [
        ('pending','Pendente'),
        ('preparing','Em preparo'),
        ('ready', 'Pronto'),
        ('delivered', 'Entregue'),
        ('canceled', 'Cancelado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    payment_status = models.BooleanField(default=False)

#Define a quantidade de itens de cada produto

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

#CART

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='cart') 
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())
    
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

# CRM 

class CRMTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#FFFFFF")
    def __str__(self):
        return self.name

class CustomerCRM(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crm_profile')
    tags = models.ManyToManyField(CRMTag, blank=True)
    internal_notes = models.TextField(blank=True, help_text="Anotações internas sobre o cliente (não visível para ele)")
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_orders_count = models.PositiveIntegerField(default=0)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    
    def update_metrics(self):
        orders = self.user.order_set.filter(payment_status=True)
        self.total_orders_count = orders.count()
        self.lifetime_value = sum(order.get_total for order in orders)
        if orders.exists():
            self.last_purchase_date = orders.latest('created_at').created_at
        self.save()

    def __str__(self):
        return f"CRM: {self.user.email}"

class CRMInteraction(models.Model):
    INTERACTION_TYPES = [
        ('call', 'Ligação'),
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('support', 'Suporte/Ticket'),
        ('meeting', 'Reunião Presencial'),
        ('other', 'Outro'),
    ]
    customer = models.ForeignKey(CustomerCRM, on_delete=models.CASCADE, related_name='interactions')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='agent_interactions') # Quem atendeu
    type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.get_type_display()} - {self.subject} ({self.created_at.strftime('%d/%m/%Y')})"

# ERP

#fornecedor

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=100, blank=True)
    phone = models.PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

#logs

class InventoryLog(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Saída'),
        ('ADJUST', 'Ajuste de Auditoria'),
    ]
    
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE, related_name='inventory_logs')
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField() 
    reason = models.CharField(max_length=200) 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
    #identifica qual tipo de produto deve ser modificado
        super().save(*args, **kwargs)
        if self.variation:
            target = self.variation
        else:
            target = self.product
            
        if self.type == 'IN':
            target.stock += self.quantity
        elif self.type == 'OUT':
            target.stock = max(0, target.stock - self.quantity)
        elif self.type == 'ADJUST':
            target.stock = self.quantity 
            pass
        target.save()
    def __str__(self):
        return f"{self.type} - {self.product.name} ({self.quantity})"
    
class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Receita'),
        ('EXPENSE', 'Despesa'),
        ]
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=200) 
    category = models.CharField(max_length=50, blank=True) 
    date = models.DateField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.get_type_display()}: R$ {self.amount} - {self.description}"











