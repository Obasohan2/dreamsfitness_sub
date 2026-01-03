from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order, SubscriptionLineItem
from blog.models import BlogPost


User = get_user_model()


# ====================================================
# PRIVATE PROFILE (OWNER ONLY)
# ====================================================
@login_required
def profile(request):
    """
    Logged-in user's private profile
    """

    # Safety: block superusers
    if request.user.is_superuser:
        messages.info(
            request,
            "Admin accounts do not have user profiles."
        )
        return redirect("home")

    profile = get_object_or_404(
        UserProfile,
        user=request.user
    )

    # Update profile
    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profile updated successfully."
            )
            return redirect("my_profile")
        else:
            messages.error(
                request,
                "Error updating profile."
            )
    else:
        form = UserProfileForm(instance=profile)

    # Order history
    orders = (
        Order.objects
        .filter(user_profile=profile)
        .order_by("-date")
    )

    # Subscription history
    subscriptions = SubscriptionLineItem.objects.filter(
        order__user_profile=profile
    )

    context = {
        "profile": profile,
        "form": form,
        "orders": orders,
        "subscriptions": subscriptions,
        "on_profile_page": True,
    }

    return render(
        request,
        "profiles/profile.html",
        context
    )


# ====================================================
# PUBLIC PROFILE (VIEWABLE BY LOGGED-IN USERS)
# ====================================================
@login_required
def public_profile(request, username):
    """
    Public-facing profile page
    """

    user = get_object_or_404(
        User,
        username=username
    )

    # Block superusers
    if user.is_superuser:
        messages.info(
            request,
            "This user does not have a public profile."
        )
        return redirect("blog")

    profile = get_object_or_404(
        UserProfile,
        user=user
    )

    posts = (
        BlogPost.objects
        .filter(author=user)
        .exclude(slug__isnull=True)
        .exclude(slug="")
        .order_by("-created_on")
    )

    context = {
        "profile_user": user,
        "profile": profile,
        "posts": posts,
    }

    return render(
        request,
        "profiles/public_profile.html",
        context
    )


# ====================================================
# ORDER HISTORY (OWNER ONLY)
# ====================================================
@login_required
def order_history(request, order_number):
    """
    View a past order from profile
    """

    order = get_object_or_404(
        Order,
        order_number=order_number,
        user_profile__user=request.user
    )

    messages.info(
        request,
        f"Viewing order {order_number}"
    )

    return render(
        request,
        "checkout/checkout_success.html",
        {
            "order": order,
            "from_profile": True,
        }
    )


# ====================================================
# SUBSCRIPTION HISTORY (OWNER ONLY)
# ====================================================
@login_required
def subscription_history(request, sub_id):
    """
    View a subscription from profile
    """

    subscription = get_object_or_404(
        SubscriptionLineItem,
        id=sub_id,
        order__user_profile__user=request.user
    )

    messages.info(
        request,
        "Viewing subscription details."
    )

    return render(
        request,
        "profiles/subscription_history.html",
        {
            "subscription": subscription,
            "from_profile": True,
        }
    )
