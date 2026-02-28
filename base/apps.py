from django.apps import AppConfig


class BaseConfig(AppConfig):
    """
    Nexum E-commerce Library Configuration
    
    This is an installable Django app that provides complete e-commerce functionality.
    
    Installation:
        pip install -e path/to/E-commerce
    
    Configuration (settings.py):
        INSTALLED_APPS = [
            ...
            'rest_framework',
            'django_filters',
            'base',  # Nexum E-commerce
        ]
        
        AUTH_USER_MODEL = 'base.BaseCustomUser'
    
    Available Models:
        - BaseProduct, ProductVariation
        - BaseCustomUser, Address, UserSecurityProfile
        - Order, OrderItem, Cart, CartItem
        - CRMTag, CustomerCRM, CRMInteraction
        - Supplier, InventoryLog, FinancialTransaction
    
    API Endpoints:
        Include in urls.py: path('api/', include('base.urls'))
    """