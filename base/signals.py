import django.dispatch
from django.dispatch import receiver

order_completed_signal = django.dispatch.Signal()
@receiver(order_completed_signal)
def update_crm_metrics(sender, user_id, order_total, order_date, **kwargs):
    from base.models import CustomerCRM
    if not user_id:
        return
        
    try:  
        crm_profile, created = CustomerCRM.objects.get_or_create(user_id=user_id)
 
        crm_profile.total_orders_count += 1
        crm_profile.lifetime_value += order_total
        if not crm_profile.last_purchase_date or order_date > crm_profile.last_purchase_date:
            crm_profile.last_purchase_date = order_date
            
        crm_profile.save()
    except Exception as e:
        pass
