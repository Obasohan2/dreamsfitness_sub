from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


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

