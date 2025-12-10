from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem, SubscriptionLineItem


@receiver(post_save, sender=OrderLineItem)
@receiver(post_delete, sender=OrderLineItem)
def update_order_totals_on_product_change(sender, instance, **kwargs):
    """
    Whenever a product line item is added/updated/deleted,
    recalculate the parent order totals.
    """
    instance.order.update_totals()


@receiver(post_save, sender=SubscriptionLineItem)
@receiver(post_delete, sender=SubscriptionLineItem)
def update_order_totals_on_subscription_change(sender, instance, **kwargs):
    """
    Whenever a subscription line item is added/updated/deleted,
    recalculate totals.
    """
    instance.order.update_totals()
