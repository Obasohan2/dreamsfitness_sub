from decimal import Decimal
from django.conf import settings


def cart_contents(request):
    """
    Safe cart context processor.
    NEVER crashes the site.
    """

    try:
        # ======================
        # PRODUCTS
        # ======================
        cart_items = []
        product_total = Decimal("0.00")
        product_count = 0

        cart = request.session.get("cart", {})

        if cart:
            from products.models import Product

            products = Product.objects.filter(id__in=cart.keys())

            for product in products:
                quantity = int(cart.get(str(product.id), 0))
                if quantity <= 0:
                    continue

                line_total = product.price * quantity

                product_total += line_total
                product_count += quantity

                cart_items.append({
                    "item_id": product.id,
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
            from subscriptions.models import SubPlan, PlanDiscount

            plan = SubPlan.objects.filter(
                pk=subscription_data.get("plan_id")
            ).first()

            if plan:
                months = max(1, int(subscription_data.get("months", 1)))
                subscription_pre_discount_total = plan.price * Decimal(months)

                discount = None
                discount_id = subscription_data.get("discount_id")

                if discount_id:
                    discount = PlanDiscount.objects.filter(
                        pk=discount_id,
                        subplan=plan
                    ).first()

                    if discount:
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
        # DELIVERY
        # ======================
        free_threshold = Decimal(settings.FREE_DELIVERY_THRESHOLD)
        delivery_percentage = Decimal(settings.STANDARD_DELIVERY_PERCENTAGE)

        if product_total > 0 and product_total < free_threshold:
            delivery = (product_total * delivery_percentage / Decimal("100"))
            free_delivery_delta = free_threshold - product_total
        else:
            delivery = Decimal("0.00")
            free_delivery_delta = Decimal("0.00")

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

    except Exception:
        return {
            "cart_items": [],
            "product_total": Decimal("0.00"),
            "product_count": 0,
            "subscription_item": None,
            "subscription_pre_discount_total": Decimal("0.00"),
            "subscription_discount_amount": Decimal("0.00"),
            "subscription_after_discount_total": Decimal("0.00"),
            "cart_count": 0,
            "delivery": Decimal("0.00"),
            "free_delivery_delta": Decimal("0.00"),
            "free_delivery_threshold": Decimal("0.00"),
            "product_grand_total": Decimal("0.00"),
            "grand_total": Decimal("0.00"),
        }
