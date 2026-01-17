from django.urls import path
from . import views

urlpatterns = [
    path("", views.BlogList, name="blog"),
    path("<int:pk>/", views.blog_detail, name="blog_detail"),
    path("post/add/", views.add_post, name="add_post"),
    path("post/edit/<int:pk>/", views.edit_post, name="edit_post"),
    path("post/delete/<int:pk>/", views.delete_post, name="delete_post"),
    path("comment/edit/<int:comment_id>/", views.edit_comment, name="edit_comment"),
    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("unlike/<int:post_id>/", views.toggle_unlike, name="toggle_unlike"),
]

