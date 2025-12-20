from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import BlogPost, Comment
# Register your models here.

admin.site.register(Comment)


@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):

    list_display = ('title', 'slug', 'created_on')
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_on',)
    summernote_fields = ('body')