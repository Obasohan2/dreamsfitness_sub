from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import OrderForm
from .models import Order, OrderLineItem, SubscriptionLineItem

from profiles.forms import UserProfileForm
from profiles.models import UserProfile

from cart.contexts import cart_contents
from subscriptions.models import SubPlan, PlanDiscount

import stripe
import json


# -------------------------------------------------------------------
# STRIPE: CACHE CHECKOUT DATA
# -------------------------------------------------------------------
@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            "cart": json.dumps(request.session.get("cart", {})),
            "subscription": json.dumps(request.session.get("subscription_cart", {})),
            "save_info": request.POST.get("save_info"),
            "username": request.user.username if request.user.is_authenticated else "guest",
        })
        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(content=e, status=400)


# -------------------------------------------------------------------
# MAIN CHECKOUT PAGE
# -------------------------------------------------------------------
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    # Save subscription selection
    if request.method == "POST" and "plan_id" in request.POST:
        request.session["subscription_cart"] = {
            "plan_id": request.POST.get("plan_id"),
            "months": int(request.POST.get("months", 1)),
            "discount_id": request.POST.get("discount_id") or None,
        }
        return redirect("checkout")

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
            "total": subscription_total,
        }

    # ---------------- FINAL TOTAL ----------------
    final_total = product_total + delivery + subscription_total

    # Stripe Intent
    client_secret = None
    if final_total > 0:
        amount = int(final_total * 100)
        intent = stripe.PaymentIntent.create(amount=amount, currency="gbp")
        client_secret = intent.client_secret

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

@require_POST
def add_subscription_to_cart(request):
    request.session["subscription_cart"] = {
        "plan_id": request.POST.get("plan_id"),
        "months": int(request.POST.get("months", 1)),
        "discount_id": request.POST.get("discount_id") or None,
    }
    return redirect("checkout")


# -------------------------------------------------------------------
# PROCESS ORDER (POST)
# -------------------------------------------------------------------
def process_order(request):

    if request.method != "POST":
        return redirect("checkout")

    cart = cart_contents(request)
    subscription = request.session.get("subscription_cart")

    if not cart["cart_items"] and not subscription:
        messages.error(request, "Your cart is empty.")
        return redirect("products")

    form = OrderForm(request.POST)
    if not form.is_valid():
        messages.error(request, "There was an error with your form.")
        return redirect("checkout")

    # --------------------------------------------
    # BUILD ORDER (WITH SHIPPING LOGIC)
    # --------------------------------------------
    order = form.save(commit=False)

    # Check if user wants a different shipping address
    use_shipping = request.POST.get("use_different_shipping") == "on"

    if not use_shipping:
        # COPY billing to shipping
        order.shipping_full_name = order.full_name
        order.shipping_phone_number = order.phone_number
        order.shipping_address1 = order.address1
        order.shipping_address2 = order.address2
        order.shipping_city = order.city
        order.shipping_postcode = order.postcode
        order.shipping_country = order.country

    order.delivery_cost = cart["delivery"]
    order.stripe_pid = request.POST.get("client_secret").split("_secret")[0]
    order.original_cart = json.dumps(request.session.get("cart", {}))
    order.save()

    # --------------------------------------------
    # PRODUCT LINE ITEMS
    # --------------------------------------------
    for item in cart["cart_items"]:
        price = Decimal(item["product"].price)
        qty = Decimal(item["quantity"])

        OrderLineItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            lineitem_total=price * qty,
        )

    # --------------------------------------------
    # SUBSCRIPTION LINE ITEM
    # --------------------------------------------
    if subscription:
        plan = get_object_or_404(SubPlan, pk=subscription["plan_id"])
        months = Decimal(subscription["months"])

        price = plan.price * months

        if subscription.get("discount_id"):
            discount = get_object_or_404(
                PlanDiscount,
                pk=subscription["discount_id"],
                subplan=plan
            )
            price -= price * Decimal(discount.total_discount) / 100

        SubscriptionLineItem.objects.create(
            order=order,
            subscription_plan=plan,
            months=int(months),
            lineitem_total=price,
        )

        order.subscription_total = price
        request.session.pop("subscription_cart", None)
    else:
        order.subscription_total = Decimal("0.00")

    # --------------------------------------------
    # UPDATE TOTALS
    # --------------------------------------------
    order.update_totals()

    # --------------------------------------------
    # CLEAR CART
    # --------------------------------------------
    request.session.pop("cart", None)

    return redirect("checkout_success", order_number=order.order_number)


# -------------------------------------------------------------------
# SUCCESS PAGE
# -------------------------------------------------------------------
def checkout_success(request, order_number):
    """ Handle successful checkout """
    save_info = request.session.get("save_info")
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.city,
                "default_street_address1": order.address1,
                "default_street_address2": order.address2,
            }
            form = UserProfileForm(profile_data, instance=profile)
            if form.is_valid():
                form.save()

    messages.success(request, f"Order {order_number} processed successfully.")

    # cleanup
    request.session.pop("cart", None)
    request.session.pop("subscription_cart", None)

    return render(request, "checkout/checkout_success.html", {
        "order": order,
        "from_profile": False,
    })