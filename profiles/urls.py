from django.urls import path
from . import views

urlpatterns = [
    # Private profile (logged-in user)
    path("", views.profile, name="my_profile"),
    
    # Public profile (authors / commenters)
    path("<str:username>/", views.public_profile, name="profile"),
    
    path("order_history/<order_number>/", views.order_history, name="order_history"),
    path("subscription_history/<int:sub_id>/", views.subscription_history, name="subscription_history"),
]
