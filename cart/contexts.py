from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from subscriptions.models import SubPlan, PlanDiscount


def cart_contents(request):
    cart_items = []
    total = Decimal("0.00")
    product_count = 0
    cart = request.session.get("cart", {})

    # ----- PRODUCTS -----
    for item_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        cart_items.append({
            "item_id": item_id,
            "quantity": quantity,
            "product": product,
        })

    # ----- SUBSCRIPTION (do NOT add into total here) -----
    subscription_data = request.session.get("subscription_cart")
    subscription_item = None
    subscription_total = Decimal("0.00")

    if subscription_data:
        plan = get_object_or_404(SubPlan, pk=subscription_data["plan_id"])
        months = int(subscription_data["months"])
        discount = None

        if subscription_data.get("discount_id"):
            discount = get_object_or_404(
                PlanDiscount,
                pk=subscription_data["discount_id"],
                subplan=plan,
            )

        subscription_total = plan.price * Decimal(months)

        if discount and discount.total_discount:
            subscription_total = subscription_total - (
                subscription_total * (discount.total_discount / Decimal("100"))
            )

        subscription_item = {
            "plan": plan,
            "months": months,
            "discount": discount,
            "total": subscription_total,
        }

    # ----- DELIVERY COST -----
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = Decimal("0.00")
        free_delivery_delta = Decimal("0.00")

    grand_total = total + delivery  # <- subscription NOT included here

    return {
        "cart_items": cart_items,
        "total": total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": grand_total,

        # subscription separate
        "subscription_item": subscription_item,
        "subscription_total": subscription_total,
    }
