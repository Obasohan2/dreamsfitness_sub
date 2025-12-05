import uuid
from django.db import models
from django.conf import settings
from django.db.models import Sum

from products.models import Product
from subscriptions.models import SubPlan  


class Order(models.Model):
    order_number = models.CharField(max_length=32, editable=False, unique=True)

    # Customer info
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    country = models.CharField(max_length=40)

    # Totals
    product_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    date = models.DateTimeField(auto_now_add=True)

    def _generate_order_number(self):
        """Generate a random, unique order number using UUID."""
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """Update totals based on ProductLineItem and SubscriptionLineItem."""
        product_total = self.product_items.aggregate(
            sum=Sum("lineitem_total")
        )["sum"] or 0

        subscription_total = self.subscription_items.aggregate(
            sum=Sum("lineitem_total")
        )["sum"] or 0

        self.product_total = product_total
        self.subscription_total = subscription_total

        order_total = product_total + subscription_total

        if order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = (
                order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
            )
        else:
            self.delivery_cost = 0

        self.grand_total = order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """Set order number on first save."""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class ProductLineItem(models.Model):
    """Normal product purchase"""
    order = models.ForeignKey(
        Order, related_name="product_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    lineitem_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)


class SubscriptionLineItem(models.Model):
    """Subscription purchase with multi-month support"""
    order = models.ForeignKey(
        "Order",
        related_name="subscription_items",
        on_delete=models.CASCADE,
    )
    subscription_plan = models.ForeignKey(SubPlan, on_delete=models.CASCADE)
    months = models.PositiveIntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.subscription_plan.title} x {self.months} months"

