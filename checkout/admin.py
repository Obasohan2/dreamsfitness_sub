from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect, get_object_or_404

from .models import Order, ProductLineItem, SubscriptionLineItem


class ProductLineItemAdminInline(admin.TabularInline):
    model = ProductLineItem
    readonly_fields = ("lineitem_total",)
    extra = 0


class SubscriptionLineItemAdminInline(admin.TabularInline):
    model = SubscriptionLineItem
    readonly_fields = ("lineitem_total",)
    extra = 0


@admin.action(description='Remove subscription from selected orders')
def remove_subscription_action(modeladmin, request, queryset):
    for order in queryset:
        SubscriptionLineItem.objects.filter(order=order).delete()
        order.update_totals()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (ProductLineItemAdminInline, SubscriptionLineItemAdminInline)
    actions = [remove_subscription_action]

    readonly_fields = (
        "order_number",
        "date",
        "display_order_total",
        "display_subscription_total",
        "display_delivery_cost",
        "display_grand_total",
    )

    list_display = (
        "order_number",
        "full_name",
        "email",
        "display_grand_total",
        "date",
    )

    fieldsets = (
        ("Order Info", {
            "fields": (
                "order_number",
                "date",
                "full_name",
                "email",
                "phone_number",
            )
        }),
        ("Delivery Details", {
            "fields": (
                "address1",
                "address2",
                "city",
                "postcode",
                "country",
            )
        }),
        ("Totals", {
            "fields": (
                "display_order_total",
                "display_subscription_total",
                "display_delivery_cost",
                "display_grand_total",
            )
        }),
    )