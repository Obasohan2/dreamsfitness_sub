from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order, SubscriptionLineItem
from blog.models import BlogPost


# ====================================================
# USER PROFILE (PRIVATE)
# ====================================================
@login_required
def profile(request):
    """
    Display user profile + order history + subscription history
    """

    # ---------- Admin safety guard ----------
    if request.user.is_superuser:
        messages.info(
            request,
            "Admin accounts do not have user profiles."
        )
        return redirect("home")

    # ---------- Get profile ----------
    profile = get_object_or_404(
        UserProfile,
        user=request.user
    )

    # ---------- Update profile ----------
    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profile updated successfully!"
            )
        else:
            messages.error(
                request,
                "Error updating your profile."
            )
    else:
        form = UserProfileForm(instance=profile)

    # ---------- Order history ----------
    orders = (
        profile.orders
        .all()
        .order_by("-date")
    )

    # ---------- Subscription history ----------
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
# PUBLIC PROFILE
# ====================================================
def public_profile(request, username):
    """
    Public-facing user profile
    """

    User = get_user_model()

    user = get_object_or_404(
        User,
        username=username
    )

    # ---------- Block superusers ----------
    if user.is_superuser:
        messages.info(
            request,
            "This user does not have a public profile."
        )
        return redirect("home")

    profile = get_object_or_404(
        UserProfile,
        user=user
    )

    # ---------- Visible posts (soft-delete aware) ----------
    posts = (
        BlogPost.objects
        .filter(
            author=user,
            is_deleted=False
        )
        .exclude(slug="")
        .exclude(slug__isnull=True)
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
# ORDER HISTORY (PROFILE ONLY)
# ====================================================
@login_required
def order_history(request, order_number):
    """
    View a past order (profile only)
    """

    order = get_object_or_404(
        Order,
        order_number=order_number,
        user_profile__user=request.user
    )

    messages.info(
        request,
        f"Viewing past order {order_number}"
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
# SUBSCRIPTION HISTORY (PROFILE ONLY)
# ====================================================
@login_required
def subscription_history(request, sub_id):
    """
    View a past subscription (profile only)
    """

    subscription = get_object_or_404(
        SubscriptionLineItem,
        id=sub_id,
        order__user_profile__user=request.user
    )

    messages.info(
        request,
        "Viewing your subscription details"
    )

    return render(
        request,
        "profiles/subscription_history.html",
        {
            "subscription": subscription,
            "from_profile": True,
        }
    )
