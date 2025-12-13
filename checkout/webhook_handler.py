from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem, SubscriptionLineItem
from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount
from profiles.models import UserProfile

import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            "checkout/confirmation_emails/confirmation_email_subject.txt",
            {"order": order},
        )
        body = render_to_string(
            "checkout/confirmation_emails/confirmation_email_body.txt",
            {"order": order, "contact_email": settings.DEFAULT_FROM_EMAIL},
        )

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email])

    # --------------------------------------------------------------------
    # GENERIC WEBHOOK EVENT
    # --------------------------------------------------------------------
    def handle_event(self, event):
        return HttpResponse(
            content=f"Unhandled webhook received: {event['type']}",
            status=200
        )

    # --------------------------------------------------------------------
    # PAYMENT INTENT SUCCEEDED
    # --------------------------------------------------------------------
    def handle_payment_intent_succeeded(self, event):
        """
        Handles successful payment webhook
        Supports:
        - Product orders
        - Subscription orders
        """
        intent = event.data.object
        pid = intent.id

        # Metadata
        cart_data = intent.metadata.cart
        subscription_data = intent.metadata.subscription
        save_info = intent.metadata.save_info
        username = intent.metadata.username

        # Billing + shipping
        billing = intent.charges.data[0].billing_details
        shipping = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean empty fields
        for key, value in shipping.address.items():
            if value == "":
                shipping.address[key] = None

        # ---------------------------------------------------------
        # ATTACH PROFILE INFO IF USER LOGGED IN
        # ---------------------------------------------------------
        profile = None
        if username != "guest" and username != "AnonymousUser":
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number = shipping.phone
                profile.default_country = shipping.address.country
                profile.default_postcode = shipping.address.postal_code
                profile.default_town_or_city = shipping.address.city
                profile.default_street_address1 = shipping.address.line1
                profile.default_street_address2 = shipping.address.line2
                profile.default_county = shipping.address.state
                profile.save()

        # ---------------------------------------------------------
        # CHECK IF ORDER EXISTS ALREADY
        # (Stripe sometimes fires webhook before redirect)
        # ---------------------------------------------------------
        order_exists = False
        attempt = 1
        order = None

        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping.name,
                    email__iexact=billing.email,
                    phone_number__iexact=shipping.phone,
                    country__iexact=shipping.address.country,
                    postcode__iexact=shipping.address.postal_code,
                    town_or_city__iexact=shipping.address.city,
                    street_address1__iexact=shipping.address.line1,
                    street_address2__iexact=shipping.address.line2,
                    county__iexact=shipping.address.state,
                    grand_total=grand_total,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        # ---------------------------------------------------------
        # ORDER EXISTS → SEND EMAIL ONLY
        # ---------------------------------------------------------
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f"Webhook {event['type']} | SUCCESS (order already exists)",
                status=200
            )

        # ---------------------------------------------------------
        # CREATE NEW ORDER FROM WEBHOOK
        # ---------------------------------------------------------
        try:
            order = Order.objects.create(
                full_name=shipping.name,
                user_profile=profile,
                email=billing.email,
                phone_number=shipping.phone,
                country=shipping.address.country,
                postcode=shipping.address.postal_code,
                town_or_city=shipping.address.city,
                street_address1=shipping.address.line1,
                street_address2=shipping.address.line2,
                county=shipping.address.state,
                grand_total=grand_total,
                original_cart=cart_data,
                original_subscription=subscription_data,
                stripe_pid=pid,
            )

            # ---------------------------------------------------------
            # PRODUCT LINE ITEMS
            # ---------------------------------------------------------
            if cart_data:
                cart = json.loads(cart_data)
                for item_id, item_data in cart.items():
                    product = Product.objects.get(id=item_id)

                    if isinstance(item_data, int):
                        OrderLineItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item_data,
                            lineitem_total=product.price * item_data,
                        )
                    else:
                        for size, qty in item_data["items_by_size"].items():
                            OrderLineItem.objects.create(
                                order=order,
                                product=product,
                                quantity=qty,
                                product_size=size,
                                lineitem_total=product.price * qty,
                            )

            # ---------------------------------------------------------
            # SUBSCRIPTION LINE ITEM
            # ---------------------------------------------------------
            if subscription_data:
                subscription_json = json.loads(subscription_data)

                plan = SubPlan.objects.get(id=subscription_json["plan_id"])
                months = int(subscription_json["months"])

                total_price = plan.price * months

                # discount
                if subscription_json.get("discount_id"):
                    discount = PlanDiscount.objects.get(
                        id=subscription_json["discount_id"],
                        subplan=plan
                    )
                    total_price -= total_price * (discount.total_discount / 100)

                SubscriptionLineItem.objects.create(
                    order=order,
                    subscription_plan=plan,
                    months=months,
                    lineitem_total=total_price,
                )

        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(
                content=f"Webhook {event['type']} | ERROR: {e}",
                status=500
            )

        # SEND EMAIL
        self._send_confirmation_email(order)

        return HttpResponse(
            content=f"Webhook {event['type']} | SUCCESS (order created)",
            status=200
        )

    # --------------------------------------------------------------------
    # PAYMENT FAILED
    # --------------------------------------------------------------------
    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f"Webhook received: {event['type']}",
            status=200
        )
