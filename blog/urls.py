from django.urls import path
from . import views

urlpatterns = [
    path("", views.BlogList, name="blog"),

    # CRUD (must come BEFORE slug route)
    path("post/add/", views.add_post, name="add_post"),
    path("post/edit/<int:pk>/", views.edit_post, name="edit_post"),
    path("post/delete/<int:pk>/", views.delete_post, name="delete_post"),

    # Comments
    path("comment/edit/<int:comment_id>/", views.edit_comment, name="edit_comment"),
    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),

    # Likes
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("unlike/<int:post_id>/", views.toggle_unlike, name="toggle_unlike"),

    # Blog post detail (slug MUST be last)
    path("<slug:slug>/", views.post_detail, name="blog_detail"),
]
