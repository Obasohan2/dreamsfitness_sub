import stripe
from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal
from .models import Order, OrderLineItem, SubscriptionLineItem
from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount
import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def handle_event(self, event):
        """Generic handler"""
        return HttpResponse(
            content=f"Unhandled event: {event['type']}",
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """Handle payment_intent.succeeded"""

        intent = event.data.object
        pid = intent.id

        cart_json = intent.metadata.get("cart", "{}")
        subscription_json = intent.metadata.get("subscription", "{}")

        # Fetch the charge (Stripe API 2024+)
        charge = stripe.Charge.retrieve(intent.latest_charge)

        billing = charge.billing_details
        shipping = intent.shipping
        grand_total = Decimal(charge.amount) / 100

        # Clean empty strings in shipping
        if shipping:
            for field, value in shipping.address.items():
                if value == "":
                    shipping.address[field] = None

        # Parse cart & subscription JSON
        cart = json.loads(cart_json)
        subscription_data = json.loads(subscription_json) if subscription_json else {}

        # ----------------------------------------------------
        # Try to find an already-created order
        # ----------------------------------------------------
        order_exists = False
        attempt = 1

        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=billing.name,
                    email__iexact=billing.email,
                    phone_number__iexact=billing.phone,
                    address1__iexact=billing.address.line1,
                    address2__iexact=billing.address.line2,
                    city__iexact=billing.address.city,
                    postcode__iexact=billing.address.postal_code,
                    country__iexact=billing.address.country,

                    shipping_full_name__iexact=shipping.name,
                    shipping_phone_number__iexact=shipping.phone,
                    shipping_address1__iexact=shipping.address.line1,
                    shipping_address2__iexact=shipping.address.line2,
                    shipping_city__iexact=shipping.address.city,
                    shipping_postcode__iexact=shipping.address.postal_code,
                    shipping_country__iexact=shipping.address.country,

                    grand_total=grand_total,
                    original_cart=cart_json,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            return HttpResponse(
                content=f"Webhook received: {event['type']} | SUCCESS: Order already exists",
                status=200
            )

        # ----------------------------------------------------
        # CREATE ORDER
        # ----------------------------------------------------
        try:
            order = Order.objects.create(
                # Billing
                full_name=billing.name,
                email=billing.email,
                phone_number=billing.phone,
                address1=billing.address.line1,
                address2=billing.address.line2,
                city=billing.address.city,
                postcode=billing.address.postal_code,
                country=billing.address.country,

                # Shipping
                shipping_full_name=shipping.name,
                shipping_phone_number=shipping.phone,
                shipping_address1=shipping.address.line1,
                shipping_address2=shipping.address.line2,
                shipping_city=shipping.address.city,
                shipping_postcode=shipping.address.postal_code,
                shipping_country=shipping.address.country,

                grand_total=grand_total,
                original_cart=cart_json,
                stripe_pid=pid,
            )

            # -----------------------------
            # PRODUCT LINE ITEMS
            # -----------------------------
            for item_id, quantity in cart.items():
                product = Product.objects.get(id=item_id)

                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    lineitem_total=product.price * quantity,
                )

            # -----------------------------
            # SUBSCRIPTION LINE ITEM
            # -----------------------------
            if subscription_data:
                plan = SubPlan.objects.get(id=subscription_data["plan_id"])
                months = int(subscription_data["months"])

                price = plan.price * months

                if subscription_data.get("discount_id"):
                    discount = PlanDiscount.objects.get(id=subscription_data["discount_id"])
                    price -= price * Decimal(discount.total_discount) / 100

                SubscriptionLineItem.objects.create(
                    order=order,
                    subscription_plan=plan,
                    months=months,
                    lineitem_total=price,
                )

        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(
                content=f"Webhook ERROR: {event['type']} | {e}",
                status=500
            )

        return HttpResponse(
            content=f"Webhook SUCCESS: {event['type']} | Order created",
            status=200
        )

    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f"Webhook received: {event['type']}",
            status=200
        )
