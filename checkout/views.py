from decimal import Decimal
import json
import stripe

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import OrderForm
from .models import Order, OrderLineItem, SubscriptionLineItem

from profiles.forms import UserProfileForm
from profiles.models import UserProfile

from cart.contexts import cart_contents
from subscriptions.models import SubPlan, PlanDiscount


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY

        subscription = request.session.get("subscription_cart", {})

        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "cart": json.dumps(request.session.get("cart", {})),
                "subscription_plan_id": str(subscription.get("plan_id", "")),
                "subscription_months": str(subscription.get("months", "")),
                "discount_id": str(subscription.get("discount_id", "")),
                "save_info": str(request.POST.get("save_info")),
                "username": (
                    request.user.username
                    if request.user.is_authenticated
                    else "AnonymousUser"
                ),
            }
        )
        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(content=str(e), status=400)


@login_required
def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_public_key = settings.STRIPE_PUBLIC_KEY

    cart = cart_contents(request)

    # Use totals computed once (single source of truth)
    product_items = cart["cart_items"]
    product_total = cart["product_total"]
    delivery = cart["delivery"]

    subscription_item = cart["subscription_item"]
    subscription_total = cart["subscription_after_discount_total"]

    grand_total = cart["grand_total"].quantize(Decimal("0.01"))

    order_form = OrderForm()

    client_secret = None
    if grand_total > 0:
        amount = int(grand_total * 100)
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="gbp",
            payment_method_types=["card"],  # Ensure only card payments are accepted
            # Optional: you can also set metadata here.
            # It will show in payment_intent.created events immediately.
            metadata={
                "cart": json.dumps(request.session.get("cart", {})),
                "subscription_plan_id": str(
                    request.session.get("subscription_cart", {}).get("plan_id", "")
                ),
                "subscription_months": str(
                    request.session.get("subscription_cart", {}).get("months", "")
                ),
                "discount_id": str(
                    request.session.get("subscription_cart", {}).get("discount_id", "")
                ),
                "username": (
                    request.user.username
                    if request.user.is_authenticated
                    else "AnonymousUser"
                ),
            }
        )
        client_secret = intent.client_secret

    context = {
        "order_form": order_form,

        # Products
        "products": product_items,
        "product_total": product_total,
        "delivery": delivery,

        # Subscription (aligned with context processor)
        "subscription_item": subscription_item,
        "subscription_total": subscription_total,
        "subscription_pre_discount_total": cart["subscription_pre_discount_total"],
        "subscription_discount_amount": cart["subscription_discount_amount"],

        # Totals
        "final_total": grand_total,   # keep your template variable name working
        "grand_total": grand_total,   # optional convenience

        # Stripe
        "stripe_public_key": stripe_public_key,
        "client_secret": client_secret,
    }

    return render(request, "checkout/checkout.html", context)


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

    order = form.save(commit=False)

    # ---------------- SHIPPING ----------------
    use_shipping = request.POST.get("use_different_shipping") == "on"

    if not use_shipping:
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

    # ---------------- PRODUCT LINE ITEMS ----------------
    for item in cart["cart_items"]:
        price = Decimal(item["product"].price)
        qty = Decimal(item["quantity"])

        OrderLineItem.objects.create(
            order=order,
            product=item["product"],
            quantity=item["quantity"],
            lineitem_total=price * qty,
        )

    # ---------------- SUBSCRIPTION LINE ITEM ----------------
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
    else:
        order.subscription_total = Decimal("0.00")

    # ---------------- FINAL TOTALS ----------------
    order.update_total()

    # ---------------- CLEAR CART ----------------
    request.session.pop("cart", None)
    request.session.pop("subscription_cart", None)

    return redirect("checkout_success", order_number=order.order_number)


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if request.session.get("save_info"):
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

    messages.success(
        request,
        f"Order {order.order_number} processed successfully!"
    )

    return render(request, "checkout/checkout_success.html", {
        "order": order,
        "from_profile": False,
    })



