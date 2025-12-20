from django import forms
from .models import SubPlan, SubPlanFeature, PlanDiscount


# ---------------------------
# Subscription Plan Form
# ---------------------------
class SubPlanForm(forms.ModelForm):
    class Meta:
        model = SubPlan
        fields = "__all__"

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than 0.")
        return price

    def clean_validity_days(self):
        days = self.cleaned_data.get("validity_days")
        if days <= 0:
            raise forms.ValidationError("Validity must be at least 1 day.")
        return days


# ---------------------------
# Subscription Plan Feature Form
# ---------------------------
class SubPlanFeatureForm(forms.ModelForm):
    class Meta:
        model = SubPlanFeature
        fields = "__all__"
        widgets = {
            "subplan": forms.CheckboxSelectMultiple(),
        }

    def clean_subplan(self):
        plans = self.cleaned_data.get("subplan")
        if not plans:
            raise forms.ValidationError("At least one plan must be selected.")
        return plans


# ---------------------------
# Plan Discount Form
# ---------------------------
class PlanDiscountForm(forms.ModelForm):
    class Meta:
        model = PlanDiscount
        fields = "__all__"

    def clean_total_months(self):
        months = self.cleaned_data.get("total_months")
        if months <= 0:
            raise forms.ValidationError("Total months must be greater than 0.")
        return months

    def clean_total_discount(self):
        discount = self.cleaned_data.get("total_discount")
        if discount <= 0 or discount > 100:
            raise forms.ValidationError("Discount must be between 1 and 100.")
        return discount

    def clean(self):
        """
        Prevent duplicate discount rules for the same plan & duration
        """
        cleaned_data = super().clean()
        subplan = cleaned_data.get("subplan")
        total_months = cleaned_data.get("total_months")

        if subplan and total_months:
            qs = PlanDiscount.objects.filter(
                subplan=subplan,
                total_months=total_months
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "A discount for this plan and duration already exists."
                )
