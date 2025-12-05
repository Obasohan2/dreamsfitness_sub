from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from subscriptions.models import SubPlan


def cart_contents(request):

    cart_items = []
    subscription_items = []

    cart = request.session.get('cart', {})
    subs = request.session.get('subscriptions', {})

    product_total = Decimal("0.00")
    subscription_total = Decimal("0.00")
    product_count = 0

    # -------------------------------
    # PRODUCT ITEMS
    # -------------------------------
    for item_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=item_id)
        subtotal = product.price * quantity

        cart_items.append({
            "item_id": item_id,
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

        product_total += subtotal
        product_count += quantity

    # -------------------------------
    # SUBSCRIPTION ITEMS
    # -------------------------------
    for plan_id in subs.keys():
        plan = get_object_or_404(SubPlan, pk=plan_id)

        subscription_items.append({
            "plan": plan,
            "price": plan.price,
        })

        subscription_total += plan.price

    # -------------------------------
    # DELIVERY CALCULATION
    # -------------------------------
    free_threshold = Decimal(str(settings.FREE_DELIVERY_THRESHOLD))
    delivery_percentage = Decimal(str(settings.STANDARD_DELIVERY_PERCENTAGE)) / Decimal("100")

    if Decimal("0.00") < product_total < free_threshold:
        delivery_cost = product_total * delivery_percentage
    else:
        delivery_cost = Decimal("0.00")

    # -------------------------------
    # GRAND TOTAL
    # -------------------------------
    grand_total = product_total + subscription_total + delivery_cost

    return {
        "cart_items": cart_items,
        "subscription_items": subscription_items,
        "product_total": product_total,
        "subscription_total": subscription_total,
        "delivery_cost": delivery_cost,
        "grand_total": grand_total,
        "product_count": product_count,
        "cart_count": product_count,  # cart bubble icon
    }

