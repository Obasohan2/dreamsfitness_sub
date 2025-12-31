from django.contrib import admin

from .models import BlogPost, Comment


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "created_on",
    )
    list_filter = (
        "created_on",
        "author",
    )
    search_fields = (
        "title",
        "body",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    ordering = (
        "-created_on",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "post",
        "created_on",
    )
    list_filter = (
        "created_on",
        "user",
    )
    search_fields = (
        "body",
        "user__username",
    )
    readonly_fields = (
        "user",
        "post",
        "created_on",
    )
    ordering = (
        "created_on",
    )

