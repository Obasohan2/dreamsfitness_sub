from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostList.as_view(), name="blog"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
    path("<slug:slug>/edit/", views.edit_post, name="edit_post"),
    path("<slug:slug>/delete/", views.delete_post, name="delete_post"),
    path("add/", views.add_post, name="add_post"),
]