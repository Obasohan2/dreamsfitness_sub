from django.urls import path
from . import views

urlpatterns = [
    # ================= PRIVATE PROFILE =================
    path(
        "",
        views.profile,
        name="my_profile",
    ),

    # ================= ORDER / SUBSCRIPTION HISTORY =================
    path(
        "order_history/<order_number>/",
        views.order_history,
        name="order_history",
    ),
    path(
        "subscription_history/<int:sub_id>/",
        views.subscription_history,
        name="subscription_history",
    ),

    # ================= PUBLIC PROFILE =================
    path(
        "<str:username>/",
        views.public_profile,
        name="profile",
    ),
]
