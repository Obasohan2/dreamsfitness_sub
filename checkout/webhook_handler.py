import stripe
import json
import time
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse

from .models import Order, OrderLineItem, SubscriptionLineItem
from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount
from profiles.models import UserProfile


class StripeWH_Handler:
    """Handle Stripe webhooks cleanly and safely"""

    def __init__(self, request):
        self.request = request
        stripe.api_key = settings.STRIPE_SECRET_KEY

    # ----------------------------------------------------
    # GENERIC CATCH-ALL EVENT HANDLER
    # ----------------------------------------------------
    def handle_event(self, event):
        return HttpResponse(
            content=f"Unhandled event type: {event['type']}",
            status=200
        )

    # ----------------------------------------------------
    # PAYMENT INTENT SUCCESS
    # ----------------------------------------------------
    def handle_payment_intent_succeeded(self, event):
        """Handle a successful payment intent"""

        intent = event.data.object
        pid = intent.id

        # Metadata (ALWAYS treat as dict)
        cart_json = intent.metadata.get("cart", "{}")
        subscription_json = intent.metadata.get("subscription", "{}")
        username = intent.metadata.get("username")
        save_info = intent.metadata.get("save_info") == "true"

        # Convert JSON to dicts
        cart = json.loads(cart_json)
        subscription_data = json.loads(subscription_json) if subscription_json else {}

        # Fetch the actual charge (required in 2024+ Stripe API)
        charge = stripe.Charge.retrieve(intent.latest_charge)

        # ----------------------------------------------------
        # BILLING INFO
        # ----------------------------------------------------
        billing = charge.billing_details
        billing_address = billing.address or {}

        # ----------------------------------------------------
        # SHIPPING INFO
        # ----------------------------------------------------
        shipping = intent.shipping
        shipping_address = shipping.address if shipping else {}

        # Clean shipping empty strings → None
        if shipping and shipping_address:
            for field, value in shipping_address.items():
                if value == "":
                    shipping_address[field] = None

        # Stripe amount is integer cents
        grand_total = Decimal(charge.amount) / Decimal("100")

        # ----------------------------------------------------
        # USER PROFILE SAVE
        # ----------------------------------------------------
        profile = None
        if username and username != "AnonymousUser":
            try:
                profile = UserProfile.objects.get(user__username=username)

                if save_info and shipping:
                    profile.default_phone_number = shipping.phone
                    profile.default_country = shipping_address.get("country")
                    profile.default_postcode = shipping_address.get("postal_code")
                    profile.default_town_or_city = shipping_address.get("city")
                    profile.default_street_address1 = shipping_address.get("line1")
                    profile.default_street_address2 = shipping_address.get("line2")
                    profile.default_county = shipping_address.get("state")
                    profile.save()

            except UserProfile.DoesNotExist:
                profile = None

        # ----------------------------------------------------
        # CHECK IF ORDER ALREADY EXISTS
        # (Race condition safe: retry 5 times)
        # ----------------------------------------------------
        order = None
        order_exists = False

        for attempt in range(5):
            try:
                order = Order.objects.get(
                    full_name__iexact=billing.name,
                    email__iexact=billing.email,
                    phone_number__iexact=billing.phone,

                    address1__iexact=billing_address.get("line1"),
                    address2__iexact=billing_address.get("line2"),
                    city__iexact=billing_address.get("city"),
                    postcode__iexact=billing_address.get("postal_code"),
                    country__iexact=billing_address.get("country"),

                    shipping_full_name__iexact=(shipping.name if shipping else None),
                    shipping_phone_number__iexact=(shipping.phone if shipping else None),
                    shipping_address1__iexact=shipping_address.get("line1") if shipping else None,
                    shipping_address2__iexact=shipping_address.get("line2") if shipping else None,
                    shipping_city__iexact=shipping_address.get("city") if shipping else None,
                    shipping_postcode__iexact=shipping_address.get("postal_code") if shipping else None,
                    shipping_country__iexact=shipping_address.get("country") if shipping else None,

                    grand_total=grand_total,
                    original_cart=cart_json,
                    stripe_pid=pid,
                )

                order_exists = True
                break

            except Order.DoesNotExist:
                time.sleep(1)

        if order_exists:
            return HttpResponse(
                content=f"Webhook: {event['type']} | SUCCESS — Order already exists",
                status=200
            )

        # ----------------------------------------------------
        # CREATE NEW ORDER
        # ----------------------------------------------------
        try:
            order = Order.objects.create(
                full_name=billing.name,
                email=billing.email,
                phone_number=billing.phone,

                address1=billing_address.get("line1"),
                address2=billing_address.get("line2"),
                city=billing_address.get("city"),
                postcode=billing_address.get("postal_code"),
                country=billing_address.get("country"),

                shipping_full_name=(shipping.name if shipping else None),
                shipping_phone_number=(shipping.phone if shipping else None),
                shipping_address1=shipping_address.get("line1") if shipping else None,
                shipping_address2=shipping_address.get("line2") if shipping else None,
                shipping_city=shipping_address.get("city") if shipping else None,
                shipping_postcode=shipping_address.get("postal_code") if shipping else None,
                shipping_country=shipping_address.get("country") if shipping else None,

                original_cart=cart_json,
                grand_total=grand_total,
                stripe_pid=pid,
                user_profile=profile if profile else None,
            )

            # ----------------------------------------------------
            # PRODUCT LINE ITEMS
            # ----------------------------------------------------
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=product_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    lineitem_total=product.price * quantity,
                )

            # ----------------------------------------------------
            # SUBSCRIPTION LINE ITEM
            # ----------------------------------------------------
            if subscription_data:
                plan = SubPlan.objects.get(id=subscription_data["plan_id"])
                months = int(subscription_data["months"])
                price = plan.price * months

                # Apply discount if present
                discount_id = subscription_data.get("discount_id")
                if discount_id:
                    discount = PlanDiscount.objects.get(id=discount_id)
                    price -= price * Decimal(discount.total_discount) / Decimal("100")

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
                content=f"Webhook ERROR during order creation: {e}",
                status=500
            )

        return HttpResponse(
            content=f"Webhook SUCCESS: {event['type']} | Order created",
            status=200
        )

    # ----------------------------------------------------
    # PAYMENT FAILED
    # ----------------------------------------------------
    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f"Webhook received: {event['type']} (payment failed)",
            status=200
        )
