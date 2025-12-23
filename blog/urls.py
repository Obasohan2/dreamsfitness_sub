from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostList.as_view(), name="blog"),
    path("create/", views.blog_create, name="blog_create"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]
