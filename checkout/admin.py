from django.contrib import admin
from .models import Order, ProductLineItem, SubscriptionLineItem


class ProductLineItemAdminInline(admin.TabularInline):
    model = ProductLineItem
    readonly_fields = ("lineitem_total",)


class SubscriptionLineItemAdminInline(admin.TabularInline):
    model = SubscriptionLineItem
    readonly_fields = ("lineitem_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (ProductLineItemAdminInline, SubscriptionLineItemAdminInline)

    # Only include fields that you KNOW exist on your Order model
    readonly_fields = (
        "order_number",
        "date",
        "full_name",
        "email",
        "phone_number",
        "country",
        "postcode",
    )

    fields = readonly_fields   # reuse the same fields

    list_display = (
        "order_number",
        "date",
        "full_name",
        "email",
    )

    ordering = ("-date",)
