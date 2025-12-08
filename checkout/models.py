from django.db import models
from products.models import Product
from subscriptions.models import SubPlan
from django_countries.fields import CountryField
from django.db.models import Sum
from decimal import Decimal
import uuid


# ----------------------------------------------------
# ORDER MODEL
# ----------------------------------------------------
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

    # Totals — all must have defaults to allow safe migrations
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Safe defaults for existing rows
    original_cart = models.TextField(default='', blank=True)
    stripe_pid = models.CharField(max_length=254, default='', blank=True)

    date = models.DateTimeField(auto_now_add=True)

    # ------------------------- Admin Display -------------------------
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

    # ------------------------- Order Logic -------------------------
    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_totals(self):
        """Recalculate totals correctly without breaking migrations."""
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

        # Safe for migrations — updates only necessary fields
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

    # Must have defaults for migration safety
    quantity = models.IntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        """Calculate total and update order safely."""
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return f'{self.product.name} (x{self.quantity}) on {self.order.order_number}'


# ----------------------------------------------------
# SUBSCRIPTION LINE ITEMS
# ----------------------------------------------------
class SubscriptionLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="subscription_items"
    )
    subscription_plan = models.ForeignKey(SubPlan, on_delete=models.CASCADE)

    # Must have defaults for safe migrations
    months = models.IntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        """Calculate subscription cost safely."""
        # Assumes SubPlan has monthly_price field
        self.lineitem_total = self.subscription_plan.monthly_price * self.months
        super().save(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return f'{self.subscription_plan.name} ({self.months} months) on {self.order.order_number}'
