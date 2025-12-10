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
        """
        Show product name + quantity in bold large font.
        Example: Kettlebells (x3)
        """
        return format_html(
            '<span style="font-size:16px; font-weight:bold;">{} (x{})</span>',
            obj.product.name,
            obj.quantity,
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
        """
        Shows subscription plan title and months.
        Example: Elite Plan (3 months)
        """
        return format_html(
            '<span style="font-size:16px; font-weight:bold;">{} ({} months)</span>',
            obj.subscription_plan.title,
            obj.months,
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
        "date",
        "display_order_total",
        "display_subscription_total",
        "display_delivery_cost",
        "display_grand_total",
        # "original_cart",
        "readable_cart",   # SHOWS PRODUCT NAMES HERE
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
                # "original_cart",
                "readable_cart",   #  ADDED THIS
                "stripe_pid",
            )
        }),
    )
    
    ordering = ("-date",)