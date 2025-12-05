from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product
from subscriptions.models import SubPlan


def view_cart(request):
    """ Render the shopping cart page """
    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add a product to the cart """

    product = get_object_or_404(Product, pk=item_id)
    cart = request.session.get('cart', {})

    # Safe quantity
    qty_raw = request.POST.get('quantity', "1")
    try:
        quantity = int(qty_raw)
    except ValueError:
        quantity = 1

    quantity = max(1, quantity)

    item_id = str(item_id)  # session keys must be strings

    # Add or update quantity
    cart[item_id] = cart.get(item_id, 0) + quantity

    # Success message
    messages.success(request, f"Added {product.name} to your cart.")

    # Save cart
    request.session['cart'] = cart

    redirect_url = request.POST.get('redirect_url') or reverse('products')
    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """ Adjust quantity of a cart item """

    product = get_object_or_404(Product, pk=item_id)
    cart = request.session.get('cart', {})

    qty_raw = request.POST.get('quantity', "1")
    try:
        quantity = int(qty_raw)
    except ValueError:
        quantity = 1

    quantity = max(1, quantity)

    item_id = str(item_id)

    # Update quantity
    cart[item_id] = quantity

    messages.success(request, f"Updated {product.name} quantity to {quantity}.")

    request.session['cart'] = cart
    return redirect(reverse("view_cart"))


def remove_from_cart(request, item_id):
    """ Remove an item from the cart """

    product = get_object_or_404(Product, pk=item_id)
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    try:
        if item_id in cart:
            del cart[item_id]
            messages.success(request, f"Removed {product.name} from your cart.")

        request.session['cart'] = cart
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f"Error removing item: {e}")
        return HttpResponse(status=500)


def add_subscription_to_cart(request, plan_id):
    """Add a subscription plan to the cart."""

    plan = get_object_or_404(SubPlan, pk=plan_id)
    subs = request.session.get("subscriptions", {})

    plan_id = str(plan_id)

    # Only one of each subscription (common practice)
    subs[plan_id] = True

    request.session["subscriptions"] = subs

    messages.success(request, f"Added subscription: {plan.title}")

    redirect_url = request.POST.get("redirect_url") or reverse("subscriptions")
    return redirect(redirect_url)


def remove_subscription_from_cart(request, plan_id):
    """Remove a subscription from the cart."""

    plan = get_object_or_404(SubPlan, pk=plan_id)
    subs = request.session.get("subscriptions", {})
    plan_id = str(plan_id)

    try:
        if plan_id in subs:
            del subs[plan_id]
            request.session["subscriptions"] = subs
            messages.success(request, f"Removed subscription: {plan.title}")
            return HttpResponse(status=200)

        return HttpResponse(status=404)

    except Exception as e:
        messages.error(request, f"Error removing subscription: {e}")
        return HttpResponse(status=500)


def remove_product(request, item_id):
    """Remove product from cart."""
    cart = request.session.get('cart', {})

    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        return HttpResponse(status=200)

    return HttpResponse(status=404)


def remove_subscription(request, plan_id):
    """Remove subscription from cart."""
    subs = request.session.get('subscriptions', {})

    if str(plan_id) in subs:
        del subs[str(plan_id)]
        request.session['subscriptions'] = subs
        return HttpResponse(status=200)

    return HttpResponse(status=404)