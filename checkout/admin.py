from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderLineItem, SubscriptionLineItem


# ---------------------------------------------------------
# PRODUCT LINE ITEMS INLINE
# ---------------------------------------------------------
class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ("lineitem_total", "display_name")
    extra = 0

    def display_name(self, obj):
        """Show product name + quantity in bold."""
        return format_html(
            '<strong style="font-size:15px;">{} (x{})</strong>',
            obj.product.name,
            obj.quantity
        )

    display_name.short_description = "Product"


# ---------------------------------------------------------
# SUBSCRIPTION LINE ITEMS INLINE
# ---------------------------------------------------------
class SubscriptionLineItemAdminInline(admin.TabularInline):
    model = SubscriptionLineItem
    readonly_fields = ("lineitem_total", "display_name")
    extra = 0

    def display_name(self, obj):
        """Show subscription plan title and duration."""
        return format_html(
            '<strong style="font-size:15px;">{} ({} months)</strong>',
            obj.subscription_plan.title,
            obj.months
        )

    display_name.short_description = "Subscription"


# ---------------------------------------------------------
# ORDER ADMIN
# ---------------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline, SubscriptionLineItemAdminInline)

    readonly_fields = (
        "order_number",
        "user_profile",
        "date",
        "display_order_total",
        "display_subscription_total",
        "display_delivery_cost",
        "display_grand_total",
        "readable_cart",
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
        ("Order Information", {
            "fields": (
                "order_number",
                "date",
                "user_profile",
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

        ("Totals & Payment", {
            "fields": (
                "display_order_total",
                "display_subscription_total",
                "display_delivery_cost",
                "display_grand_total",
                "readable_cart",
                "stripe_pid",
            )
        }),
    )

    ordering = ("-date",)
