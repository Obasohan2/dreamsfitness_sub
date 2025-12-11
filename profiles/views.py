from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order, SubscriptionLineItem


@login_required
def profile(request):
    """ Display user profile + orders + subscriptions """
    profile = get_object_or_404(UserProfile, user=request.user)

    # --- Update profile form ---
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Error updating your profile.")
    else:
        form = UserProfileForm(instance=profile)

    # --- Order history ---
    orders = profile.orders.all().order_by("-date")

    # --- Subscription history ---
    subscriptions = SubscriptionLineItem.objects.filter(order__user_profile=profile)

    context = {
        "form": form,
        "orders": orders,
        "subscriptions": subscriptions,
        "on_profile_page": True,
    }

    return render(request, "profiles/profile.html", context)


@login_required
def order_history(request, order_number):
    """ View a past order inside profile """
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, f"Viewing past order {order_number}")

    return render(request, "checkout/checkout_success.html", {
        "order": order,
        "from_profile": True,
    })


@login_required
def subscription_history(request, sub_id):
    """ View a past subscription inside profile """
    subscription = get_object_or_404(SubscriptionLineItem, id=sub_id)

    messages.info(request, "Viewing your subscription details")

    return render(request, "profiles/subscription_history.html", {
        "subscription": subscription,
        "from_profile": True,
    })
