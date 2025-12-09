from django.db import models
from products.models import Product
from subscriptions.models import SubPlan
from django_countries.fields import CountryField
from django.db.models import Sum
from decimal import Decimal
import uuid


class Order(models.Model):
    # ---------------- Billing fields ----------------
    order_number = models.CharField(max_length=32, editable=False)
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address1 = models.CharField(max_length=80)
    address2 = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=40)
    postcode = models.CharField(max_length=20)
    country = CountryField()

    # ---------------- Shipping fields ----------------
    shipping_full_name = models.CharField(max_length=50, blank=True, null=True)
    shipping_phone_number = models.CharField(max_length=20, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=80, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=80, blank=True, null=True)
    shipping_city = models.CharField(max_length=40, blank=True, null=True)
    shipping_postcode = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = CountryField(blank=True, null=True)

    # ---------------- Totals ----------------
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ---------------- Meta Info ----------------
    original_cart = models.TextField(default='', blank=True)
    stripe_pid = models.CharField(max_length=254, default='', blank=True)
    date = models.DateTimeField(auto_now_add=True)

    # ---------------- Admin Display Helpers ----------------
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

    # ---------------- Methods ----------------
    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_totals(self):
        product_total = (
            self.lineitems.aggregate(total=Sum("lineitem_total"))["total"]
            or Decimal("0.00")
        )

        subscription_total = (
            self.subscription_items.aggregate(total=Sum("lineitem_total"))["total"]
            or Decimal("0.00")
        )

        self.order_total = product_total
        self.subscription_total = subscription_total
        self.grand_total = (
            product_total + subscription_total + Decimal(self.delivery_cost)
        )

        self.save(update_fields=[
            "order_total",
            "subscription_total",
            "grand_total",
        ])

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


# ----------------------------------------------------
# PRODUCT LINE ITEMS
# ----------------------------------------------------
class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='lineitems'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) on {self.order.order_number}"


# ----------------------------------------------------
# SUBSCRIPTION LINE ITEMS
# ----------------------------------------------------
class SubscriptionLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="subscription_items"
    )
    subscription_plan = models.ForeignKey(SubPlan, on_delete=models.CASCADE)

    months = models.IntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Using monthly_price from SubPlan
        self.lineitem_total = self.subscription_plan.monthly_price * self.months
        super().save(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return (
            f"{self.subscription_plan.name} ({self.months} months) "
            f"on {self.order.order_number}"
        )
