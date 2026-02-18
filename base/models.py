from django.db import models

#DOCUMENTATION ABOUT ID'S
import uuid

#DOCUMENTATION ABOUT USER'S
from django.contrib.auth.models import AbstractUser
#aponta para o modelo correto de usuario
from django.conf import settings

#PRODUCTS

class BaseProduct(models.Model):
    name = models.CharField(max_length=125)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=300)
    slug = models.SlugField(unique=True) #(category)

#USERS

class Address(models.Model):
    street = models.CharField(max_length=255)
    number = models.PositiveIntegerField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

class BaseCustomUser(AbstractUser):
    name = models.CharField(max_length=125)
    phone = models.PhoneNumberField(blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)

# ORDERS 

class Order(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.AutoField()
    @property
    def get_total(self):   
        #Soma o valor total do pedido multiplicando o preço de cada produto pela sua quantidade e somando todos os itens.
        #Retorna:
        #valor total do pedido
        return sum(item.product.price * item.quantity for item in self.items.all())
    @property
    def get_products_and_quantities(self): 
    #Retorna uma lista de tuplas (produto, quantidade) deste pedido.
    #Exemplo de uso:
    #    for produto, quantidade in order.get_products_and_quantities():
    #        print(produto.name, quantidade)
        return [(item.product, item.quantity) for item in self.items.all()]
    @property
    def get_total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())
    STATUS_CHOICE = [
        ('pending','Pendente'),
        ('preparing','Em preparo'),
        ('ready', 'Pronto')
    ]
    status = models.CharField(max_length=20)

#Define a quantidade de itens de cada produto

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
#CART

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return sum(item['product'].price * item['quantity'] for item in self.items.values())
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(BaseProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)