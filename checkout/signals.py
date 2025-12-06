from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_order_totals(sender, instance, **kwargs):
    """
    Recalculate totals whenever an Order or its LineItems change.
    """

    # PRODUCT LINE ITEMS
    product_total = sum(
        item.lineitem_total for item in instance.product_items.all()
    )

    # SUBSCRIPTION LINE ITEMS
    subscription_total = sum(
        item.lineitem_total for item in instance.subscription_items.all()
    )

    # Delivery Cost (if present, else 0)
    delivery_cost = getattr(instance, "delivery_cost", 0)

    # Final grand total
    grand_total = product_total + subscription_total + delivery_cost

    # Save values efficiently (no recursion)
    Order.objects.filter(id=instance.id).update(
        order_total=product_total,
        subscription_total=subscription_total,
        grand_total=grand_total
    )
