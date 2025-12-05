import uuid
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Order


def generate_order_number():
    """Generate a random unique order number"""
    return uuid.uuid4().hex.upper()


@receiver(pre_save, sender=Order)
def add_order_number(sender, instance, **kwargs):
    """
    Add a unique order number before saving
    """
    if not instance.order_number:
        instance.order_number = generate_order_number()


@receiver(post_save, sender=Order)
def update_order_totals(sender, instance, **kwargs):
    """
    Recalculate totals after saving an order.

    Supports:
    ✔ Product-only orders
    ✔ Subscription-only orders
    ✔ Mixed orders
    """

    lineitems = instance.lineitems.all()

    # PRODUCT TOTAL
    product_total = sum(item.lineitem_total for item in lineitems)

    # SUBSCRIPTION TOTAL
    subscription_total = instance.subscription_price or 0

    # UPDATE ORDER TOTALS
    instance.order_total = product_total
    instance.grand_total = product_total + subscription_total + instance.delivery_cost

    # Prevent repeat saves
    Order.objects.filter(id=instance.id).update(
        order_total=instance.order_total,
        grand_total=instance.grand_total
    )
