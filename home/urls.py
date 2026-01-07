from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path("terms/", views.terms, name="terms"),
    path("nutrition-guides/", views.nutrition_guides, name="nutrition_guides"),
]