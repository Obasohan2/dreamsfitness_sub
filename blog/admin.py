from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import BlogPost, Comment


@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):
    list_display = ("title", "author", "created_on")
    search_fields = ("title", "body")
    list_filter = ("created_on",)
    prepopulated_fields = {"slug": ("title",)}
    summernote_fields = ("body",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "created_on")
    list_filter = ("created_on",)
    search_fields = ("name", "email", "body")
    readonly_fields = ("name", "email", "body", "post", "created_on")