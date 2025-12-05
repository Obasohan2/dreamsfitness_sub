from django.urls import path
from . import views

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("sub_checkout/<int:plan_id>/", views.sub_checkout, name="sub_checkout"),
    # path("add/<int:plan_id>/", views.add_to_cart, name="add_to_cart"),
    # path("remove/<int:plan_id>/", views.remove_from_cart, name="remove_from_cart"),
]
