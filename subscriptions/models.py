from django.db import models


# ---------------------------
# Subscription Plans
# ---------------------------
class SubPlan(models.Model):
    title = models.CharField(max_length=150)
    price = models.PositiveIntegerField()
    max_member = models.PositiveIntegerField(null=True, blank=True)
    highlight_status = models.BooleanField(default=False)
    validity_days = models.PositiveIntegerField(null=True, blank=True)

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
    total_months = models.PositiveIntegerField()
    total_discount = models.PositiveIntegerField()

    def __str__(self):
        return str(self.total_months)
