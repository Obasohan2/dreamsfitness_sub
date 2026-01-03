from django.contrib import admin

from .models import BlogPost, Comment, Category


# ====================================================
# CATEGORY ADMIN
# ====================================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    ordering = (
        "name",
    )


# ====================================================
# BLOG POST ADMIN
# ====================================================
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "is_success_story",
        "created_on",
    )

    list_filter = (
        "category",
        "is_success_story",
        "created_on",
        "author",
    )

    search_fields = (
        "title",
        "body",
        "author__username",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    ordering = (
        "-created_on",
    )

    raw_id_fields = (
        "author",
    )

    fieldsets = (
        (
            "Post Content",
            {
                "fields": (
                    "title",
                    "slug",
                    "body",
                    "image",
                )
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "category",
                    "is_success_story",
                )
            },
        ),
        (
            "Author & Metadata",
            {
                "fields": (
                    "author",
                    "created_on",
                )
            },
        ),
    )

    readonly_fields = (
        "created_on",
    )


# ====================================================
# COMMENT ADMIN
# ====================================================
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
        "post__title",
    )

    readonly_fields = (
        "user",
        "post",
        "created_on",
    )

    ordering = (
        "created_on",
    )
