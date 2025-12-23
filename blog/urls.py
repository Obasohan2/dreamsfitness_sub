from django.urls import path
from . import views

urlpatterns = [
    # Blog list
    path("", views.PostList.as_view(), name="blog"),

    # Add post (before slug routes)
    path("add/", views.add_post, name="add_post"),

    # Reactions (before slug routes)
    path(
        "react/<int:post_id>/<str:reaction>/",
        views.toggle_reaction,
        name="toggle_reaction"
    ),

    # Slug-based routes LAST
    path("<slug:slug>/edit/", views.edit_post, name="edit_post"),
    path("<slug:slug>/delete/", views.delete_post, name="delete_post"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]
