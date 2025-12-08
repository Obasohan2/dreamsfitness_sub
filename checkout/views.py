from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import OrderForm
from .models import Order, ProductLineItem, SubscriptionLineItem
from cart.contexts import cart_contents
from subscriptions.models import SubPlan, PlanDiscount

import stripe
import json


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)

# -------------------------------------------------------------------
# CHECKOUT VIEW
# -------------------------------------------------------------------

def checkout(request):
    """ Handle the checkout page """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    stripe.api_key = stripe_secret_key     
    

    # ---------------- SAVE SUBSCRIPTION INTO SESSION ----------------
    if request.method == "POST" and "plan_id" in request.POST:
        request.session["subscription_cart"] = {
            "plan_id": request.POST.get("plan_id"),
            "months": int(request.POST.get("months", 1)),
            "discount_id": request.POST.get("discount_id") or None,
        }
        return redirect("checkout")

    # ---------------- CART DATA ----------------
    cart = cart_contents(request)
    order_form = OrderForm()

    products = cart["cart_items"]
    product_total = cart["total"]
    delivery = cart["delivery"]

    # ---------------- SUBSCRIPTION ----------------
    subscription_data = request.session.get("subscription_cart")
    subscription_detail = None
    subscription_total = Decimal("0.00")

    if subscription_data:
        plan = get_object_or_404(SubPlan, pk=subscription_data["plan_id"])
        months = int(subscription_data["months"])
        discount_id = subscription_data.get("discount_id")

        subscription_total = plan.price * Decimal(months)
        discount_obj = None

        if discount_id:
            discount_obj = get_object_or_404(PlanDiscount, pk=discount_id)
            subscription_total -= subscription_total * (Decimal(discount_obj.total_discount) / 100)

        subscription_detail = {
            "plan": plan,
            "months": months,
            "discount": discount_obj,
            "discount_id": discount_id,
            "total": subscription_total,
        }

    # ---------------- FINAL TOTAL ----------------
    final_total = product_total + delivery + subscription_total

    # ---------------- STRIPE PAYMENT INTENT ----------------

    intent = None
    client_secret = None

    if final_total > 0:
        amount = int((final_total * Decimal("100")).quantize(Decimal("1")))
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="gbp",
        )
        client_secret = intent.client_secret

    # ---------------- RENDER ----------------
    return render(request, "checkout/checkout.html", {
        "order_form": order_form,
        "products": products,
        "product_total": product_total,
        "delivery": delivery,
        "subscription": subscription_detail,
        "subscription_total": subscription_total,
        "final_total": final_total,
        "stripe_public_key": stripe_public_key,
        "client_secret": client_secret,
    })


# -------------------------------------------------------------------
# PROCESS ORDER VIEW
# -------------------------------------------------------------------

def process_order(request):

    if request.method != "POST":
        return redirect("checkout")

    cart = cart_contents(request)
    subscription = request.session.get("subscription_cart")

    form = OrderForm(request.POST)
    if not form.is_valid():
        messages.error(request, "There was an error with your form.")
        return redirect("checkout")

    # ---------------- CREATE ORDER BASE ----------------
    order = form.save(commit=False)

    # Convert delivery cost to Decimal safely
    order.delivery_cost = Decimal(cart["delivery"])
    order.save()

    # ---------------- PRODUCT ITEMS ----------------
    for item in cart["cart_items"]:

        # Always convert to Decimal to avoid float issues
        price = Decimal(str(item["product"].price))
        quantity = Decimal(item["quantity"])

        ProductLineItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            lineitem_total=price * quantity,
        )

    # ---------------- SUBSCRIPTION ITEM ----------------
    order.subscription_total = Decimal("0.00")

    if subscription:
        plan = get_object_or_404(SubPlan, pk=subscription["plan_id"])

        months = Decimal(subscription["months"])
        price = plan.price * months  # plan.price is already Decimal

        discount_id = subscription.get("discount_id")
        if discount_id:
            discount = get_object_or_404(PlanDiscount, pk=discount_id)
            price -= price * (Decimal(discount.total_discount) / Decimal("100"))

        SubscriptionLineItem.objects.create(
            order=order,
            subscription_plan=plan,
            months=int(months),
            lineitem_total=price,
        )

        order.subscription_total = price

        request.session.pop("subscription_cart", None)

    # ---------------- CALCULATE & SAVE TOTALS ----------------
    order.update_totals()
    order.save()

    # ---------------- CLEAR CART ----------------
    request.session.pop("cart", None)

    return redirect("checkout_success", order_number=order.order_number)


# -------------------------------------------------------------------
# SUCCESS PAGE
# -------------------------------------------------------------------
def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(
        request,
        f"Payment successful! Your order {order_number} has been completed."
    )

    return render(request, "checkout/checkout_success.html", {
        "order": order,
    })