from django.db import models
from products.models import Product
from subscriptions.models import SubPlan
from django_countries.fields import CountryField
from django.db.models import Sum
from django.conf import settings
import uuid
from decimal import Decimal

import locale
locale.setlocale(locale.LC_ALL, '')


class Order(models.Model):
    order_number = models.CharField(max_length=32, editable=False)
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address1 = models.CharField(max_length=80)
    address2 = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=40)
    postcode = models.CharField(max_length=20)
    country = CountryField()

    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    date = models.DateTimeField(auto_now_add=True)

    # ----------------------------------------------------
    # DISPLAY METHODS FOR ADMIN TABLE
    # ----------------------------------------------------
    def display_order_total(self):
        return f"£{self.order_total:.2f}"
    display_order_total.short_description = "Order Total"

    def display_subscription_total(self):
        return f"£{self.subscription_total:.2f}"
    display_subscription_total.short_description = "Subscription Total"

    def display_delivery_cost(self):
        return f"£{self.delivery_cost:.2f}"
    display_delivery_cost.short_description = "Delivery Cost"

    def display_grand_total(self):
        return f"£{self.grand_total:.2f}"
    display_grand_total.short_description = "Grand Total"

    # ----------------------------------------------------
    # ORDER LOGIC
    # ----------------------------------------------------
    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_totals(self):
        """Recalculate totals safely."""
        product_total = (
            self.product_items.aggregate(total=Sum("lineitem_total"))["total"]
            or Decimal("0.00")
        )

        subscription_total = (
            self.subscription_items.aggregate(total=Sum("lineitem_total"))["total"]
            or Decimal("0.00")
        )

        delivery_cost = Decimal(self.delivery_cost or 0)

        self.order_total = product_total
        self.subscription_total = subscription_total
        self.delivery_cost = delivery_cost
        self.grand_total = product_total + subscription_total + delivery_cost

        self.save(update_fields=[
            "order_total",
            "subscription_total",
            "delivery_cost",
            "grand_total",
        ])

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class ProductLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="product_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2)


class SubscriptionLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="subscription_items"
    )
    subscription_plan = models.ForeignKey(SubPlan, on_delete=models.CASCADE)
    months = models.IntegerField()
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2)


