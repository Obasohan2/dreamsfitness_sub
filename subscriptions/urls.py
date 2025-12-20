from django.urls import path
from . import views

urlpatterns = [
    # PUBLIC
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/<int:plan_id>/", views.sub_checkout, name="sub_checkout"),

    # ADMIN
    path("admin/", views.subscription_admin_dashboard, name="subscription_admin_dashboard"),
    path("admin/add/", views.add_subscription_plan, name="add_subscription_plan"),
    path("admin/edit/<int:plan_id>/", views.edit_subscription_plan, name="edit_subscription_plan"),
    path("admin/delete/<int:plan_id>/", views.delete_subscription_plan, name="delete_subscription_plan"),
]
