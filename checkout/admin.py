from django.contrib import admin
from .models import Order, OrderLineItem, SubscriptionLineItem


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ("lineitem_total",)


class SubscriptionLineItemInline(admin.TabularInline):
    model = SubscriptionLineItem
    readonly_fields = ("lineitem_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    inlines = (OrderLineItemInline, SubscriptionLineItemInline)

    readonly_fields = (
        "order_number",
        "date",
        "order_total",
        "subscription_total",
        "delivery_cost",
        "grand_total",
        "original_cart",
        "stripe_pid",
    )

    fields = (
        "order_number",
        "user_profile",
        "date",
        "full_name",
        "email",
        "phone_number",
        "address1",
        "address2",
        "city",
        "postcode",
        "country",
        "shipping_full_name",
        "shipping_phone_number",
        "shipping_address1",
        "shipping_address2",
        "shipping_city",
        "shipping_postcode",
        "shipping_country",
        "order_total",
        "subscription_total",
        "delivery_cost",
        "grand_total",
        "original_cart",
        "stripe_pid",
    )

    list_display = (
        "order_number",
        "date",
        "full_name",
        "grand_total",
    )

    ordering = ("-date",)
