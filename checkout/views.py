from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
import stripe

from .forms import OrderForm
from cart.contexts import cart_contents
from subscriptions.models import SubPlan, PlanDiscount


stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout(request):

    # 1) Handle subscription POST
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

    # 2) Build checkout summary
    cart = cart_contents(request)
    order_form = OrderForm()

    products = cart["cart_items"]
    product_total = cart["total"]
    delivery = cart["delivery"]

    subscription = request.session.get("subscription_cart")
    subscription_detail = None
    subscription_total = Decimal("0")

    if subscription:
        plan = get_object_or_404(SubPlan, pk=subscription["plan_id"])
        months = int(subscription["months"])
        discount_id = subscription.get("discount_id")

        subscription_total = plan.price * Decimal(months)

        if discount_id:
            discount = get_object_or_404(PlanDiscount, pk=discount_id)
            subscription_total -= subscription_total * (Decimal(discount.total_discount) / 100)

        subscription_detail = {
            "plan": plan,
            "months": months,
            "discount_id": discount_id,
            "total": subscription_total,
        }

    final_total = product_total + delivery + subscription_total

    # 3) Create Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=int(final_total * 100),  # convert £ → pence
        currency="gbp",
    )

    # 4) Render template WITH context
    context = {
        "order_form": order_form,
        "products": products,
        "product_total": product_total,
        "delivery": delivery,
        "subscription": subscription_detail,
        "subscription_total": subscription_total,
        "final_total": final_total,

        # ---------- Stripe keys ----------
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "client_secret": intent.client_secret,
    }

    return render(request, "checkout/checkout.html", context)










# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from decimal import Decimal

# from .forms import OrderForm
# from cart.contexts import cart_contents

# from subscriptions.models import SubPlan, PlanDiscount


# def checkout(request):
#     """
#     Handles:
#     - POST from subscription selection → saves subscription_cart into session
#     - Displays final checkout page (products + subscription)
#     """

#     # --------------------------------------------------
#     # 1) Handle subscription POST from sub_checkout.html
#     # --------------------------------------------------
#     if request.method == "POST" and "plan_id" in request.POST:

#         plan_id = request.POST.get("plan_id")
#         months = int(request.POST.get("months", 1))
#         discount_id = request.POST.get("discount_id") or None

#         # Save subscription to session
#         request.session["subscription_cart"] = {
#             "plan_id": plan_id,
#             "months": months,
#             "discount_id": discount_id,
#         }

#         return redirect("checkout")  # Load final checkout summary

#     # --------------------------------------------------
#     # 2) Build final combined checkout summary
#     # --------------------------------------------------
#     cart = cart_contents(request)
#     order_form = OrderForm()

#     products = cart["cart_items"]
#     product_total = cart["total"]
#     delivery = cart["delivery"]

#     # ---------------- SUBSCRIPTION ----------------
#     subscription = request.session.get("subscription_cart")
#     subscription_detail = None
#     subscription_total = Decimal("0")

#     if subscription:
#         plan = get_object_or_404(SubPlan, pk=subscription["plan_id"])
#         months = int(subscription["months"])
#         discount_id = subscription.get("discount_id")

#         # Base subscription price
#         subscription_total = plan.price * Decimal(months)

#         # Apply discount if selected
#         if discount_id:
#             discount = get_object_or_404(PlanDiscount, pk=discount_id)
#             subscription_total -= subscription_total * (Decimal(discount.total_discount) / 100)

#         subscription_detail = {
#             "plan": plan,
#             "months": months,
#             "discount_id": discount_id,
#             "total": subscription_total,
#         }

#     # --------------- FINAL TOTAL -----------------
#     final_total = product_total + delivery + subscription_total

#     return render(request, "checkout/checkout.html", {
#         "order_form": order_form,
#         "products": products,
#         "product_total": product_total,
#         "delivery": delivery,
#         "subscription": subscription_detail,
#         "subscription_total": subscription_total,
#         "final_total": final_total,
        
#         # --- Stripe ---
#     })


# def process_order(request):
#     """ Creates Order + Product LineItems + Subscription LineItem """

#     if request.method != "POST":
#         return redirect("checkout")

#     cart = cart_contents(request)
#     subscription = request.session.get("subscription_cart")

#     form = OrderForm(request.POST)
#     if not form.is_valid():
#         messages.error(request, "There was an error in your billing form.")
#         return redirect("checkout")

#     order = form.save(commit=False)
#     order.save()

#     # ---------------- PRODUCTS -----------------
#     from .models import ProductLineItem
#     for item in cart["cart_items"]:
#         ProductLineItem.objects.create(
#             order=order,
#             product=item["product"],
#             quantity=item["quantity"],
#             lineitem_total=item["product"].price * item["quantity"],
#         )

#     # ---------------- SUBSCRIPTION -------------
#     if subscription:
#         from .models import SubscriptionLineItem

#         plan = get_object_or_404(SubPlan, pk=subscription["plan_id"])
#         months = int(subscription["months"])
#         discount_id = subscription.get("discount_id")

#         price = plan.price * Decimal(months)

#         if discount_id:
#             discount = get_object_or_404(PlanDiscount, pk=discount_id)
#             price -= price * (Decimal(discount.total_discount) / 100)

#         SubscriptionLineItem.objects.create(
#             order=order,
#             subscription_plan=plan,
#             months=months,
#             lineitem_total=price,
#         )

#         # Remove subscription from session after purchase
#         del request.session["subscription_cart"]

#     # ---------------- CLEAR PRODUCT CART ----------------
#     if "cart" in request.session:
#         del request.session["cart"]

#     return redirect("checkout_success", order_number=order.order_number)


# def checkout_success(request, order_number):
#     return render(request, "checkout/checkout_success.html", {
#         "order_number": order_number,
#     })
