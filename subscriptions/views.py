from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from decimal import Decimal

from .models import SubPlan, SubPlanFeature, PlanDiscount


# -------------------------------------------------
# PRICING PAGE
# -------------------------------------------------
def pricing(request):
    plans = SubPlan.objects.all()
    dfeatures = SubPlanFeature.objects.all()

    subscription = request.session.get("subscription_cart")
    selected_plan_id = subscription.get("plan_id") if subscription else None

    for plan in plans:
        plan.is_selected = (plan.id == selected_plan_id)

    return render(request, "subscriptions/pricing.html", {
        "plans": plans,
        "dfeatures": dfeatures,
    })


# -------------------------------------------------
# SUBSCRIPTION CHECKOUT
# -------------------------------------------------
def sub_checkout(request, plan_id):
    """Show checkout page for a selected subscription plan."""

    plan = get_object_or_404(SubPlan, pk=plan_id)

    features = SubPlanFeature.objects.filter(subplan=plan)
    discounts = plan.discounts.all()

    # -----------------------------
    # POST → Save selection
    # -----------------------------
    if request.method == "POST":

        months = int(request.POST.get("validity", 0))
        discount_id = request.POST.get("discount_id")

        if months <= 0:
            messages.error(request, "Please select a subscription duration.")
            return redirect("sub_checkout", plan_id=plan.id)

        discount = None
        if discount_id:
            discount = get_object_or_404(
                PlanDiscount,
                pk=discount_id,
                subplan=plan
            )

        total_price = plan.price * Decimal(months)

        if discount and discount.total_discount:
            total_price -= total_price * (Decimal(discount.total_discount) / 100)

        # Save to session
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
    # GET → Render checkout page
    # -----------------------------
    return render(request, "subscriptions/sub_checkout.html", {
        "plan": plan,
        "features": features,
        "discounts": discounts,
    })


@staff_member_required
def subscription_admin_dashboard(request):
    context = {
        "plans": SubPlan.objects.all(),
        "features": SubPlanFeature.objects.all(),
        "discounts": PlanDiscount.objects.all(),
        "highlighted_plan": SubPlan.objects.filter(highlight_status=True).first(),
    }
    return render(request, "admin/subscriptions_dashboard.html", context)