from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import SubPlan, SubPlanFeature, PlanDiscount
from decimal import Decimal


def pricing(request):
    """Display all plans + comparison table."""
    plans = SubPlan.objects.all()
    dfeatures = SubPlanFeature.objects.all()

    return render(request, "subscriptions/pricing.html", {
        "plans": plans,
        "dfeatures": dfeatures,
    })


def sub_checkout(request, plan_id):
    """Show checkout page for a selected subscription plan and store selection in session."""
    plan = get_object_or_404(SubPlan, pk=plan_id)

    # Features & Discounts
    features = SubPlanFeature.objects.filter(subplan=plan)
    discounts = plan.discounts.all()

    # -----------------------------
    # POST → User selects duration
    # -----------------------------
    if request.method == "POST":

        months = int(request.POST.get("validity", 0))
        discount_id = request.POST.get("discount_id")

        if months <= 0:
            messages.error(request, "Please select a subscription duration.")
            return redirect("sub_checkout", plan_id=plan.id)

        # Fetch discount (if exists)
        discount = None
        if discount_id:
            discount = get_object_or_404(
                PlanDiscount, 
                pk=discount_id, 
                subplan=plan
            )

        # Base price
        total_price = plan.price * Decimal(months)

        # Apply discount
        if discount and discount.total_discount:
            total_price -= total_price * (Decimal(discount.total_discount) / Decimal("100"))

        # Save into session
        request.session["subscription_cart"] = {
            "plan_id": plan.id,
            "months": months,
            "discount_id": discount.id if discount else None,
        }

        messages.success(
            request,
            f"{plan.title} ({months} month{'s' if months > 1 else ''}) added to your cart."
        )

        return redirect("checkout")

    # -----------------------------
    # GET → Display plan checkout
    # -----------------------------
    return render(request, "subscriptions/sub_checkout.html", {
        "plan": plan,
        "features": features,
        "discounts": discounts,
    })
