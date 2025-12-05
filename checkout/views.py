from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Order, ProductLineItem, SubscriptionLineItem
from .forms import OrderForm
from products.models import Product
from subscriptions.models import SubPlan

from cart.contexts import cart_contents  # to access cart data



def checkout(request, plan_id=None):
    """
    Display checkout page for a selected plan.
    Allow removing the selected plan from inside checkout.
    """

    # If user clicked "remove plan"
    if request.GET.get("remove") == "1":
        # No cart → simply redirect back to pricing page
        return redirect("pricing")

    # If no plan_id → also redirect
    if plan_id is None:
        messages.error(request, "Please select a subscription plan.")
        return redirect("pricing")

    # Load plan
    plan = get_object_or_404(SubPlan, id=plan_id)

    # Member stats
    registered = plan.subscriptionlineitem.count()
    balance = plan.max_member - registered

    return render(request, "checkout.html", {
        "plan": plan,
        "registered": registered,
        "balance": balance,
        "features": plan.subplanfeature.all(),
        "discounts": plan.discounts.all(),
    })
    

def checkout_success(request, order_number):
    """
    Display the checkout success page.
    """
    return render(request, "checkout/checkout_success.html", {
        "order_number": order_number
    })
