from django.urls import path

from . import views


urlpatterns = [
    # Blog list
    path(
        "",
        views.PostList.as_view(),
        name="blog",
    ),

    # Add post
    path(
        "add/",
        views.add_post,
        name="add_post",
    ),

    # Comment routes (MUST be before slug routes)
    path(
        "comment/edit/<int:comment_id>/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "comment/delete/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),

    # Reactions (AJAX ONLY)
    path(
        "reaction/",
        views.post_reaction,
        name="post_reaction",
    ),

    # Post routes (LAST)
    path(
        "<slug:slug>/edit/",
        views.edit_post,
        name="edit_post",
    ),
    path(
        "<slug:slug>/delete/",
        views.delete_post,
        name="delete_post",
    ),
    path(
        "<slug:slug>/",
        views.post_detail,
        name="post_detail",
    ),
]
