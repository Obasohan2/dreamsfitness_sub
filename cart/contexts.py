from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404

from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount


def cart_contents(request):
    """
    Makes cart contents available to all templates
    (products + subscription).
    """

    # ======================
    # PRODUCTS
    # ======================
    cart_items = []
    product_total = Decimal("0.00")
    product_count = 0

    cart = request.session.get("cart", {})

    for item_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=item_id)
        quantity = int(quantity)
        line_total = product.price * quantity

        product_total += line_total
        product_count += quantity

        cart_items.append({
            "item_id": item_id,
            "quantity": quantity,
            "product": product,
            "line_total": line_total,
        })

    # ======================
    # SUBSCRIPTION
    # ======================
    subscription_data = request.session.get("subscription_cart")
    subscription_item = None

    subscription_pre_discount_total = Decimal("0.00")
    subscription_discount_amount = Decimal("0.00")
    subscription_after_discount_total = Decimal("0.00")

    if subscription_data:
        plan = get_object_or_404(SubPlan, pk=subscription_data["plan_id"])
        months = max(1, int(subscription_data.get("months", 1)))

        subscription_pre_discount_total = plan.price * Decimal(months)

        discount = None
        if subscription_data.get("discount_id"):
            discount = get_object_or_404(
                PlanDiscount,
                pk=subscription_data["discount_id"],
                subplan=plan
            )
            subscription_discount_amount = (
                subscription_pre_discount_total *
                Decimal(discount.total_discount) / Decimal("100")
            )

        subscription_after_discount_total = (
            subscription_pre_discount_total - subscription_discount_amount
        )

        subscription_item = {
            "plan": plan,
            "months": months,
            "discount": discount,
        }

    # ======================
    # DELIVERY (PRODUCTS ONLY)
    # ======================
    free_threshold = Decimal(settings.FREE_DELIVERY_THRESHOLD)
    delivery_percentage = Decimal(settings.STANDARD_DELIVERY_PERCENTAGE)

    if product_total > 0:
        if product_total < free_threshold:
            delivery = (product_total * delivery_percentage / Decimal("100"))
            free_delivery_delta = free_threshold - product_total
        else:
            delivery = Decimal("0.00")
            free_delivery_delta = Decimal("0.00")
    else:
        delivery = Decimal("0.00")
        free_delivery_delta = None

    # ======================
    # TOTALS
    # ======================
    product_grand_total = (product_total + delivery).quantize(Decimal("0.01"))
    grand_total = (
        product_grand_total + subscription_after_discount_total
    ).quantize(Decimal("0.01"))

    return {
        # Products
        "cart_items": cart_items,
        "product_total": product_total,
        "product_count": product_count,

        # Subscription
        "subscription_item": subscription_item,
        "subscription_pre_discount_total": subscription_pre_discount_total,
        "subscription_discount_amount": subscription_discount_amount,
        "subscription_after_discount_total": subscription_after_discount_total,

        # Counts
        "cart_count": product_count + (1 if subscription_item else 0),

        # Delivery
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": free_threshold,

        # Totals
        "product_grand_total": product_grand_total,
        "grand_total": grand_total,
    }
