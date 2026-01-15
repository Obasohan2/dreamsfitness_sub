from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostList.as_view(), name="blog"),
    path("add/", views.add_post, name="add_post"),
    path("reaction/", views.post_reaction, name="post_reaction"),
    path("<slug:slug>/edit/", views.edit_post, name="edit_post"),
    path("<slug:slug>/delete/", views.delete_post, name="delete_post"),
    path("comment/<int:comment_id>/edit/", views.edit_comment, name="edit_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]
