from django.shortcuts import render, redirect
from django.urls import reverse

def view_cart(request):
    """ A view that renders the cart contents page """
    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add a quantity of the specified product to the shopping cart """

    # Safe quantity handling
    quantity = int(request.POST.get('quantity', 1))

    # Redirect back to previous page or fallback to product list
    redirect_url = request.POST.get('redirect_url') or reverse('products')

    cart = request.session.get('cart', {})

    # Convert item_id to string because session keys are strings
    item_id = str(item_id)

    if item_id in cart:
        cart[item_id] += quantity
    else:
        cart[item_id] = quantity

    request.session['cart'] = cart

    print("Updated cart:", request.session['cart'])

    return redirect(redirect_url)
