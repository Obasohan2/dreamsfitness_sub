from django.contrib import admin
from .models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "consent",
        "is_active",
        "subscribed_at",
    )
    list_filter = (
        "is_active",
        "consent",
    )
    search_fields = ("email",)
    list_editable = ("is_active",)
    ordering = ("-subscribed_at",)
