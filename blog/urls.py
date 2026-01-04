from django.urls import path
from . import views

urlpatterns = [
    # ====================================================
    # BLOG LISTS
    # ====================================================
    path(
        "",
        views.PostList.as_view(),
        name="blog",
    ),
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostList.as_view(),
        name="category_posts",
    ),

    # ====================================================
    # POST CRUD
    # ====================================================
    path(
        "add/",
        views.add_post,
        name="add_post",
    ),

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

    # ====================================================
    # COMMENTS
    # ====================================================
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

    # ====================================================
    # REACTIONS (AJAX)
    # ====================================================
    path(
        "reaction/",
        views.post_reaction,
        name="post_reaction",
    ),

    # ====================================================
    # POST DETAIL (LAST – IMPORTANT)
    # ====================================================
    path(
        "<slug:slug>/",
        views.post_detail,
        name="post_detail",
    ),
]
