from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile, name="profile"),
    path("order_history/<order_number>/", views.order_history, name="order_history"),
    path("subscription_history/<int:sub_id>/", views.subscription_history, name="subscription_history"),
]
