from django.urls import path
from .import views
from .views import PostList

urlpatterns = [
    path('', PostList.as_view(), name='blog'),
]
