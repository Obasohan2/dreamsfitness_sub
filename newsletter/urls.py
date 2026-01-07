from django.urls import path
from . import views

urlpatterns = [
    path("", views.subscribe_newsletter, name="newsletter_subscribe"),
]
