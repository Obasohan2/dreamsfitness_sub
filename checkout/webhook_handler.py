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

    def handle_event(self, event):
        return HttpResponse(
            content=f"Unhandled webhook received: {event['type']}",
            status=200
        )

    # -----------------------------------------------------------
    # PAYMENT INTENT SUCCEEDED
    # -----------------------------------------------------------
    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id

        metadata = intent.metadata or {}
        cart_json = metadata.get("cart")
        save_info = metadata.get("save_info")

        if not cart_json:
            return HttpResponse("No cart metadata found.", status=200)

        cart = json.loads(cart_json)

        # Billing info
        billing = intent.charges.data[0].billing_details
        name = billing.name
        email = billing.email
        phone = billing.phone

        grand_total = Decimal(intent.amount) / 100

        # -------------------------------------------------------
        # TRY TO FIND ORDER CREATED BY process_order()
        # -------------------------------------------------------
        order = None
        for _ in range(5):
            try:
                order = Order.objects.get(
                    full_name__iexact=name,
                    email__iexact=email,
                    phone_number__iexact=phone,
                    grand_total=grand_total,
                    stripe_pid=pid,
                )
                return HttpResponse(
                    content=f"Webhook received: {event['type']} | SUCCESS: Order already exists",
                    status=200
                )
            except Order.DoesNotExist:
                time.sleep(1)

        # -------------------------------------------------------
        # IF NOT FOUND, CREATE ORDER FROM WEBHOOK
        # -------------------------------------------------------
        try:
            order = Order.objects.create(
                full_name=name,
                email=email,
                phone_number=phone,
                address1="Provided at checkout",
                address2="",
                city="Provided at checkout",
                postcode="Provided at checkout",
                country="GB",
                original_cart=cart_json,
                stripe_pid=pid,
                delivery_cost=Decimal("0.00"),
            )

            # ------------------------
            # PRODUCT LINE ITEMS
            # ------------------------
            for item in cart.get("cart_items", []):
                product = Product.objects.get(id=item["product_id"])
                qty = Decimal(item["quantity"])
                price = Decimal(str(product.price))

                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=int(qty),
                    lineitem_total=qty * price,
                )

            # ------------------------
            # SUBSCRIPTION LINE ITEM
            # ------------------------
            subscription = cart.get("subscription")
            if subscription:
                plan = SubPlan.objects.get(id=subscription["plan_id"])
                months = Decimal(subscription["months"])
                price = plan.price * months

                discount_id = subscription.get("discount_id")
                if discount_id:
                    discount = PlanDiscount.objects.get(id=discount_id)
                    price -= price * (Decimal(discount.total_discount) / 100)

                SubscriptionLineItem.objects.create(
                    order=order,
                    subscription_plan=plan,
                    months=int(months),
                    lineitem_total=price
                )

            # Update final totals
            order.update_totals()

        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(
                content=f"Webhook error: {e}",
                status=500
            )

        return HttpResponse(
            content=f"Webhook received: {event['type']} | SUCCESS: Order created by webhook",
            status=200
        )

    # -----------------------------------------------------------
    # PAYMENT FAILED
    # -----------------------------------------------------------
    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f"Webhook received: {event['type']}",
            status=200
        )
