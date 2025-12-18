from decimal import Decimal
import json
import time

from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from subscriptions.models import SubPlan
from profiles.models import UserProfile
from cart.contexts import cart_contents


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    # ------------------------------------------------
    # EMAIL
    # ------------------------------------------------
    def _send_confirmation_email(self, order):
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        )

        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {
                "order": order,
                "contact_email": settings.DEFAULT_FROM_EMAIL,
            },
        )

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
        )

    # ------------------------------------------------
    # DEFAULT HANDLER
    # ------------------------------------------------
    def handle_event(self, event):
        return HttpResponse(
            content=f"Unhandled webhook received: {event['type']}",
            status=200,
        )

    # ------------------------------------------------
    # PAYMENT SUCCESS
    # ------------------------------------------------
    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id

        metadata = intent.metadata
        cart_json = metadata.get("cart", "{}")
        username = metadata.get("username", "AnonymousUser")

        subscription_plan_id = metadata.get("subscription_plan_id")
        subscription_months = metadata.get("subscription_months")

        # ------------------------------------------------
        # REBUILD CART FROM METADATA
        # ------------------------------------------------
        cart_data = json.loads(cart_json)

        # Inject cart into session for cart_contents()
        self.request.session["cart"] = cart_data

        # Restore subscription cart if present
        if subscription_plan_id:
            self.request.session["subscription_cart"] = {
                "plan_id": subscription_plan_id,
                "months": subscription_months,
                "discount_id": metadata.get("discount_id"),
            }

        cart_totals = cart_contents(self.request)
        grand_total = cart_totals["grand_total"].quantize(Decimal("0.01"))

        # ------------------------------------------------
        # STRIPE AMOUNT VERIFICATION (SECURITY)
        # ------------------------------------------------
        stripe_amount = Decimal(intent.amount) / Decimal("100")

        if stripe_amount != grand_total:
            return HttpResponse(
                content="Amount mismatch – possible tampering detected",
                status=400,
            )

        # ------------------------------------------------
        # BILLING / SHIPPING
        # ------------------------------------------------
        charge = intent.charges.data[0]
        billing_details = charge.billing_details
        shipping_details = intent.shipping

        # Clean empty address fields
        if shipping_details and shipping_details.address:
            for field, value in shipping_details.address.items():
                if value == "":
                    shipping_details.address[field] = None

        # ------------------------------------------------
        # USER PROFILE
        # ------------------------------------------------
        profile = None
        if username != "AnonymousUser":
            profile = UserProfile.objects.get(user__username=username)

        # ------------------------------------------------
        # CHECK IF ORDER EXISTS (IDEMPOTENCY)
        # ------------------------------------------------
        order_exists = False
        attempt = 1

        while attempt <= 5:
            try:
                order = Order.objects.get(
                    stripe_pid=pid,
                    original_cart=cart_json,
                    grand_total=grand_total,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f"Webhook received: {event['type']} | Order already exists",
                status=200,
            )

        # ------------------------------------------------
        # CREATE ORDER
        # ------------------------------------------------
        try:
            order = Order.objects.create(
                full_name=shipping_details.name,
                user_profile=profile,
                email=billing_details.email,
                phone_number=shipping_details.phone,
                country=shipping_details.address.country,
                postcode=shipping_details.address.postal_code,
                town_or_city=shipping_details.address.city,
                street_address1=shipping_details.address.line1,
                street_address2=shipping_details.address.line2,
                grand_total=grand_total,
                original_cart=cart_json,
                stripe_pid=pid,
            )

            # ------------------------------------------------
            # SUBSCRIPTION
            # ------------------------------------------------
            if subscription_plan_id:
                plan = SubPlan.objects.get(id=subscription_plan_id)
                order.subscription_plan = plan
                order.subscription_months = int(subscription_months)
                order.subscription_total = cart_totals[
                    "subscription_after_discount_total"
                ]
                order.save()

            # ------------------------------------------------
            # PRODUCTS
            # ------------------------------------------------
            for item_id, quantity in cart_data.items():
                product = Product.objects.get(id=item_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )

        except Exception as e:
            if order:
                order.delete()

            return HttpResponse(
                content=f"Webhook received: {event['type']} | ERROR: {e}",
                status=500,
            )

        # ------------------------------------------------
        # CONFIRMATION EMAIL
        # ------------------------------------------------
        self._send_confirmation_email(order)

        return HttpResponse(
            content=f"Webhook received: {event['type']} | Order created successfully",
            status=200,
        )

    # ------------------------------------------------
    # PAYMENT FAILED
    # ------------------------------------------------
    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f"Webhook received: {event['type']}",
            status=200,
        )
