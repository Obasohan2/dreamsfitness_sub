from django.db import models


# ---------------------------
# Subscription Plans
# ---------------------------
class SubPlan(models.Model):
    title = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    max_member = models.PositiveIntegerField(null=True, blank=True)
    highlight_status = models.BooleanField(default=False)
    validity_days = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.title


# ---------------------------
# Subscription Plan Features
# ---------------------------
class SubPlanFeature(models.Model):
    subplan = models.ManyToManyField(SubPlan)
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title


# ---------------------------
# Package Discounts
# ---------------------------
class PlanDiscount(models.Model):
    subplan = models.ForeignKey(
        SubPlan,
        related_name="discounts",
        on_delete=models.CASCADE
    )
    total_months = models.IntegerField()
    total_discount = models.IntegerField()

    def __str__(self):
        return str(self.total_months)


# ---------------------------
# PURCHASED SUBSCRIPTION
# ---------------------------
class Subscription(models.Model):
    order = models.ForeignKey(
        "checkout.Order",
        related_name="subscriptions",
        on_delete=models.CASCADE
    )
    subscription_plan = models.ForeignKey(
        SubPlan,
        on_delete=models.CASCADE
    )
    months = models.PositiveIntegerField()
    lineitem_total = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.subscription_plan.title} ({self.months} months)"
