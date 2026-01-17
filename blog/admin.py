from django.contrib import admin
from .models import BlogPost, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_on")
    list_filter = ("created_on", "category")
    search_fields = ("title", "content")
    ordering = ("-created_on",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "blog_post", "created_on")
    ordering = ("-created_on",)
