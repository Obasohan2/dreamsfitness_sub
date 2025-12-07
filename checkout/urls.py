from django.urls import path
from . import views


urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("process/", views.process_order, name="process_order"),
    path("success/<order_number>/", views.checkout_success, name="checkout_success"),

]
