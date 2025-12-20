from django.db import models
from products.models import Product
from django_countries.fields import CountryField
from decimal import Decimal
import uuid
import json
from profiles.models import UserProfile


# ====================================================
# ORDER
# ====================================================
class Order(models.Model):

    # ---------------- Billing fields ----------------
    order_number = models.CharField(max_length=32, editable=False)
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    full_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address1 = models.CharField(max_length=80)
    address2 = models.CharField(max_length=80, blank=True, null=True)
    city = models.CharField(max_length=40)
    postcode = models.CharField(max_length=20)
    country = CountryField(blank_label='Country', null=False, blank=False)

    # ---------------- Shipping fields ----------------
    shipping_full_name = models.CharField(max_length=50, blank=True, null=True)
    shipping_phone_number = models.CharField(max_length=20, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=80, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=80, blank=True, null=True)
    shipping_city = models.CharField(max_length=40, blank=True, null=True)
    shipping_postcode = models.CharField(max_length=20, blank=True, null=True)
    shipping_country = CountryField(blank_label='Country', null=False, blank=False)

    # ---------------- Totals ----------------
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subscription_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ---------------- Meta ----------------
    original_cart = models.TextField(default='', blank=True)
    stripe_pid = models.CharField(max_length=254, default='', blank=True)
    date = models.DateTimeField(auto_now_add=True)

    # ---------------- Helpers ----------------
    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    @property
    def has_subscription(self):
        return self.subscription_total > Decimal("0.00")

    def update_total(self):
        self.order_total = sum(
            item.lineitem_total for item in self.lineitems.all()
        ) or Decimal("0.00")

        self.subscription_total = sum(
            sub.lineitem_total for sub in self.subscription_items.all()
        ) or Decimal("0.00")

        self.grand_total = (
            self.order_total +
            self.subscription_total +
            self.delivery_cost
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

    def readable_cart(self):
        try:
            cart = json.loads(self.original_cart)
        except Exception:
            return "Invalid cart data"

        lines = []
        for product_id, qty in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                lines.append(f"{product.name} × {qty}")
            except Product.DoesNotExist:
                lines.append(f"Unknown product (ID {product_id}) × {qty}")

        return "\n".join(lines)

    readable_cart.short_description = "Original Cart"


# ====================================================
# PRODUCT LINE ITEMS
# ====================================================
class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='lineitems'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"


# ====================================================
# SUBSCRIPTION LINE ITEMS
# ====================================================
class SubscriptionLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="subscription_items"
    )
    subscription_plan = models.ForeignKey(
        "subscriptions.SubPlan",
        on_delete=models.CASCADE
    )
    months = models.PositiveIntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        monthly_cost = self.subscription_plan.price
        total = monthly_cost * self.months

        discount = self.subscription_plan.discounts.filter(
            total_months=self.months
        ).first()

        if discount:
            total -= (total * Decimal(discount.total_discount) / 100)

        self.lineitem_total = total
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f"{self.subscription_plan.title} ({self.months} months)"
