from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product
from subscriptions.models import SubPlan


# -----------------------------
# VIEW CART
# -----------------------------
def view_cart(request):
    """ Render the shopping cart page """
    return render(request, 'cart/cart.html')


# -----------------------------
# PRODUCT CART FUNCTIONS
# -----------------------------
def add_to_cart(request, item_id):
    """ Add a product to the cart """

    product = get_object_or_404(Product, pk=item_id)
    cart = request.session.get('cart', {})

    qty_raw = request.POST.get('quantity', "1")
    try:
        quantity = int(qty_raw)
    except ValueError:
        quantity = 1

    quantity = max(1, quantity)
    item_id = str(item_id)

    cart[item_id] = cart.get(item_id, 0) + quantity

    messages.success(request, f"Added {product.name} to your cart.")

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

    cart[item_id] = quantity
    messages.success(request, f"Updated {product.name} quantity to {quantity}.")
    request.session['cart'] = cart

    return redirect(reverse("view_cart"))


def remove_from_cart(request, item_id):
    """ Remove a product from the cart """

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


# -----------------------------
# SUBSCRIPTION CART FUNCTIONS
# -----------------------------
def add_subscription_to_cart(request, plan_id):
    """Add a subscription plan to the cart (only one at a time)."""

    plan = get_object_or_404(SubPlan, pk=plan_id)

    # Subscription stored as a SINGLE object
    request.session["subscription_cart"] = {
        "plan_id": plan.id
    }

    messages.success(request, f"Added subscription: {plan.title}")

    redirect_url = request.POST.get("redirect_url") or reverse("pricing")
    return redirect(redirect_url)


def remove_subscription_from_cart(request):
    """Remove subscription from cart."""

    if "subscription_cart" in request.session:
        del request.session["subscription_cart"]
        messages.success(request, "Subscription removed from your cart.")

    return redirect("view_cart")
