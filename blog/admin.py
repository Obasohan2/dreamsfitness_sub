from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import BlogPost, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):
    list_display = ("title", "author", "created_on")
    list_filter = ("created_on", "categories")
    search_fields = ("title", "content")
    filter_horizontal = ("categories",)
    summernote_fields = ("content",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "blog_post", "created_on")
    list_filter = ("created_on",)
    search_fields = ("name", "email", "body")

