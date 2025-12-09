from django.contrib import admin
from .models import Order, OrderLineItem, SubscriptionLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ("lineitem_total",)
    extra = 0


class SubscriptionLineItemAdminInline(admin.TabularInline):
    model = SubscriptionLineItem
    readonly_fields = ("lineitem_total",)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline, SubscriptionLineItemAdminInline)

    readonly_fields = (
        "order_number",
        "date",
        "display_order_total",
        "display_subscription_total",
        "display_delivery_cost",
        "display_grand_total",
        "original_cart",
        "stripe_pid",
    )

    list_display = (
        "order_number",
        "date",
        "full_name",
        "email",
        "display_grand_total",
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

        ("Billing Address", {
            "fields": (
                "address1",
                "address2",
                "city",
                "postcode",
                "country",
            )
        }),

        ("Shipping Address", {
            "fields": (
                "shipping_full_name",
                "shipping_phone_number",
                "shipping_address1",
                "shipping_address2",
                "shipping_city",
                "shipping_postcode",
                "shipping_country",
            )
        }),

        ("Totals", {
            "fields": (
                "display_order_total",
                "display_subscription_total",
                "display_delivery_cost",
                "display_grand_total",
                "original_cart",
                "stripe_pid",
            )
        }),
    )
