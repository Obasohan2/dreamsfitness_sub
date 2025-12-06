from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.conf import settings

from .forms import OrderForm
from cart.contexts import cart_contents
from subscriptions.models import SubPlan, PlanDiscount

import stripe


def checkout(request):
   
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    """
    Handles:
    - POST from subscription selection → saves subscription_cart into session
    - Displays combined checkout page (products + subscription)
    """

    # --------------------------------------------------
    # 1) Handle subscription POST → save to session
    # --------------------------------------------------
    if request.method == "POST" and "plan_id" in request.POST:
        plan_id = request.POST.get("plan_id")
        months = int(request.POST.get("months", 1))
        discount_id = request.POST.get("discount_id") or None

        request.session["subscription_cart"] = {
            "plan_id": plan_id,
            "months": months,
            "discount_id": discount_id,
        }

        return redirect("checkout")

    # --------------------------------------------------
    # 2) Build combined checkout summary
    # --------------------------------------------------
    cart = cart_contents(request)
    order_form = OrderForm()

    products = cart["cart_items"]
    product_total = cart["total"]
    delivery = cart["delivery"]

    # ---------------- SUBSCRIPTION ----------------
    subscription_data = request.session.get("subscription_cart")
    subscription_detail = None
    subscription_total = Decimal("0")

    if subscription_data:
        plan = get_object_or_404(SubPlan, pk=subscription_data["plan_id"])
        months = int(subscription_data["months"])
        discount_id = subscription_data.get("discount_id")

        subscription_total = plan.price * Decimal(months)

        if discount_id:
            discount = get_object_or_404(PlanDiscount, pk=discount_id)
            subscription_total -= subscription_total * (
                Decimal(discount.total_discount) / 100
            )

        subscription_detail = {
            "plan": plan,
            "months": months,
            "discount_id": discount_id,
            "total": subscription_total,
        }

    # ---------------- FINAL TOTAL -----------------
    final_total = product_total + delivery + subscription_total

    # ---------------- STRIPE PAYMENT INTENT ----------------
    stripe.api_key = stripe_secret_key

    intent = stripe.PaymentIntent.create(
        amount=int(final_total * 100),  # Stripe uses pence
        currency="gbp",
    )

    # --------------------------------------------------
    # Render checkout page
    # --------------------------------------------------
    return render(request, "checkout/checkout.html", {
        "order_form": order_form,
        "products": products,
        "product_total": product_total,
        "delivery": delivery,
        "subscription": subscription_detail,
        "subscription_total": subscription_total,
        "final_total": final_total,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
    })


def process_order(request):
    """ Creates Order + Product LineItems + Subscription LineItem """

    if request.method != "POST":
        return redirect("checkout")

    cart = cart_contents(request)
    subscription = request.session.get("subscription_cart")

    form = OrderForm(request.POST)
    if not form.is_valid():
        messages.error(request, "There was an error in your billing form.")
        return redirect("checkout")

    order = form.save(commit=False)
    order.save()

    # ---------------- PRODUCTS -----------------
    from .models import ProductLineItem
    for item in cart["cart_items"]:
        ProductLineItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            lineitem_total=item["product"].price * item["quantity"],
        )

    # ---------------- SUBSCRIPTION -------------
    if subscription:
        from .models import SubscriptionLineItem

        plan = get_object_or_404(SubPlan, pk=subscription["plan_id"])
        months = int(subscription["months"])
        discount_id = subscription.get("discount_id")

        price = plan.price * Decimal(months)

        if discount_id:
            discount = get_object_or_404(PlanDiscount, pk=discount_id)
            price -= price * (Decimal(discount.total_discount) / 100)

        SubscriptionLineItem.objects.create(
            order=order,
            subscription_plan=plan,
            months=months,
            lineitem_total=price,
        )

        # Clear subscription session data
        del request.session["subscription_cart"]

    # ---------------- CLEAR PRODUCT CART ----------------
    if "cart" in request.session:
        del request.session["cart"]

    return redirect("checkout_success", order_number=order.order_number)


def checkout_success(request, order_number):
    return render(request, "checkout/checkout_success.html", {
        "order_number": order_number,
    })
