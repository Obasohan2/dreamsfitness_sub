from django.urls import path
from . import views


urlpatterns = [
    path("", views.checkout, name="checkout"),
    path("process/", views.process_order, name="process_order"),
    path("success/<order_number>/", views.checkout_success, name="checkout_success"),
]


# urlpatterns = [
#     path('', views.checkout, name='checkout'),
#     path("checkout/<int:plan_id>/", views.checkout, name="checkout"),
#     path('<int:plan_id>/', views.checkout, name='checkout'),
#     path("success/<order_number>/", views.checkout_success, name="checkout_success"),
#     path("process/", views.process_order, name="process_order"),

# ]
