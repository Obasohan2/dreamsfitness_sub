from django.db import models
from products.models import Product
from subscriptions.models import SubPlan
from django_countries.fields import CountryField
from django.db.models import Sum
from decimal import Decimal
import uuid
import json
from profiles.models import UserProfile


class Order(models.Model):
    # ---------------- Billing fields ----------------
    order_number = models.CharField(max_length=32, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='orders')
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

    # ---------------- Meta Info ----------------
    original_cart = models.TextField(default='', blank=True)
    stripe_pid = models.CharField(max_length=254, default='', blank=True)
    date = models.DateTimeField(auto_now_add=True)

    # ---------------- Admin Display Helper (Formatter) ----------------
    def _currency(self, value):
        """Formats any numeric value as £XX.XX"""
        return f"£{value:.2f}"

    # Mapping used to generate helper methods dynamically
    _DISPLAY_FIELDS = {
        "display_order_total": ("order_total", "Order Total"),
        "display_subscription_total": ("subscription_total", "Subscription Total"),
        "display_delivery_cost": ("delivery_cost", "Delivery Cost"),
        "display_grand_total": ("grand_total", "Grand Total"),
    }

    # Create the display methods dynamically
    for method_name, (field_name, label) in _DISPLAY_FIELDS.items():
        def make_display(field):
            return lambda self: self._currency(getattr(self, field))
        func = make_display(field_name)
        func.short_description = label
        locals()[method_name] = func

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

    # ---------------- Readable Cart ----------------
    def readable_cart(self):
        """
        Convert original_cart JSON into readable product names + quantities.
        """
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
        return f"{self.product.name} (x{self.quantity})"


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
        monthly_cost = self.subscription_plan.price  
        total = monthly_cost * self.months

        discount = self.subscription_plan.discounts.filter(
            total_months=self.months
        ).first()

        if discount:
            discount_amount = (total * discount.total_discount) / 100
            total -= discount_amount

        self.lineitem_total = total

        super().save(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return f"{self.subscription_plan.title} ({self.months} months)"

