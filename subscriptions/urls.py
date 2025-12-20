from django.urls import path
from .views import subscription_admin_dashboard
from . import views

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("sub_checkout/<int:plan_id>/", views.sub_checkout, name="sub_checkout"),
    path("admin/subscriptions/", subscription_admin_dashboard, name="subscription_admin_dashboard"),
]
