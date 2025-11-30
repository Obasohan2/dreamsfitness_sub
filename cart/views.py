# from django.shortcuts import render, redirect, reverse, HttpResponse
# from django.contrib import messages

# from products.models import Product


# def view_cart(request):
#     """Render the shopping cart page."""
#     return render(request, 'cart/cart.html')


# def add_to_cart(request, item_id):
#     """Add a product to the cart."""
    
#     product = Product.objects.get(pk=item_id)
    
#     cart = request.session.get('cart', {})

#     # Safe quantity conversion
#     qty_raw = request.POST.get('quantity', "1")
#     try:
#         quantity = int(qty_raw)
#     except ValueError:
#         quantity = 1

#     quantity = max(1, quantity)  # enforce minimum 1

#     # Convert key to string for session consistency
#     item_id = str(item_id)

#     # Add or increase
#     cart[item_id] = cart.get(item_id, 0) + quantity

#     request.session['cart'] = cart

#     redirect_url = request.POST.get('redirect_url') or reverse('products')
#     return redirect(redirect_url)


# def adjust_cart(request, item_id):
#     """Adjust the quantity of a specific cart item."""
#     cart = request.session.get('cart', {})

#     qty_raw = request.POST.get('quantity', "1")

#     # Safe integer conversion
#     try:
#         quantity = int(qty_raw)
#     except ValueError:
#         quantity = 1

#     quantity = max(1, quantity)  # enforce minimum quantity

#     item_id = str(item_id)

#     # Update quantity
#     cart[item_id] = quantity

#     request.session['cart'] = cart
#     return redirect(reverse('view_cart'))


# def remove_from_cart(request, item_id):
#     """Remove an item from the cart."""
#     try:
#         cart = request.session.get('cart', {})
#         item_id = str(item_id)

#         if item_id in cart:
#             del cart[item_id]

#         request.session['cart'] = cart
#         return HttpResponse(status=200)

#     except Exception:
#         return HttpResponse(status=500)


from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import messages
from products.models import Product


def view_cart(request):
    """Render the cart page."""
    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """Add an item to the cart with quantity handling."""

    product = Product.objects.get(pk=item_id)

    cart = request.session.get('cart', {})

    # Safe quantity parsing
    qty_raw = request.POST.get('quantity', "1")
    try:
        quantity = int(qty_raw)
    except ValueError:
        quantity = 1

    quantity = max(1, quantity)  # Prevent 0 or negative

    item_id = str(item_id)

    # Add or increment
    cart[item_id] = cart.get(item_id, 0) + quantity

    request.session['cart'] = cart

    messages.success(request, f"Added {product.name} to cart.")

    redirect_url = request.POST.get('redirect_url') or reverse('products')
    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """Adjust item quantity (never below 1)."""

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

    request.session['cart'] = cart
    messages.info(request, "Cart updated.")
    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id):
    """Remove item completely from cart."""
    try:
        cart = request.session.get('cart', {})
        item_id = str(item_id)

        if item_id in cart:
            del cart[item_id]
            request.session['cart'] = cart

        return HttpResponse(status=200)

    except Exception:
        return HttpResponse(status=500)

