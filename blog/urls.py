from django.urls import path
from . import views

urlpatterns = [
    path("", views.BlogList, name="blog"),

    # Posts
    path("post/add/", views.add_post, name="add_post"),
    path("post/edit/<int:pk>/", views.edit_post, name="edit_post"),
    path("post/delete/<int:pk>/", views.delete_post, name="delete_post"),

    # Comments
    path("comment/edit/<int:comment_id>/", views.edit_comment, name="edit_comment"),
    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),

    # Reactions
    path("like/<int:pk>/", views.toggle_like, name="toggle_like"),
    path("unlike/<int:pk>/", views.toggle_unlike, name="toggle_unlike"),

    # Detail (last)
    path("<slug:slug>/", views.blog_detail, name="blog_detail"),
]
