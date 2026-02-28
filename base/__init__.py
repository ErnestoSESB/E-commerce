"""
Nexum E-commerce Library
========================

A Django-based e-commerce library providing complete functionality for:
- Product management (products, variations, inventory)
- User management (custom user model, addresses, security)
- Order processing (orders, order items, carts)
- CRM (customer relationship management)
- Financial tracking (transactions, supplier management)

Quick Start
-----------
Add 'base' to your INSTALLED_APPS in settings.py:

    INSTALLED_APPS = [
        ...
        'rest_framework',
        'django_filters',
        'base',
    ]

Configure the custom user model:

    AUTH_USER_MODEL = 'base.CustomUser'

Include the URLs in your project:

    from django.urls import path, include
    
    urlpatterns = [
        path('api/', include('base.urls')),
    ]

Run migrations:

    python manage.py migrate

Usage
-----
Import models directly:

    from base.models import BaseProduct, Order, Cart
    
    # Create a product
    product = BaseProduct.objects.create(
        name="Example Product",
        price=99.99,
        stock=100
    )

Import serializers:

    from base.serializers import ProductSerializer
    
    serializer = ProductSerializer(product)

Import viewsets:

    from base.views import BaseProductViewSet
"""

__version__ = '0.1.0'
__author__ = 'Your Name'

# Django app configuration
default_app_config = 'base.apps.BaseConfig'
