from django.db import models
from products.models import Product
from subscriptions.models import SubPlan
from django_countries.fields import CountryField
import uuid
from decimal import Decimal

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

    date = models.DateTimeField(auto_now_add=True)

    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class ProductLineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class SubscriptionLineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubPlan, on_delete=models.CASCADE)
    months = models.IntegerField()
    lineitem_total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.subscription_plan.title} ({self.months} months)"



