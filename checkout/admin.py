from django.contrib import admin
from .models import Order, ProductLineItem, SubscriptionLineItem
# Register your models here.


class ProductLineItemAdminInline(admin.TabularInline):
    model = ProductLineItem
    readonly_fields = ('lineitem_total',)
    extra = 0


class SubscriptionLineItemAdminInline(admin.TabularInline):
    model = SubscriptionLineItem
    readonly_fields = ('lineitem_total',)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    inlines = (ProductLineItemAdminInline, SubscriptionLineItemAdminInline)

    readonly_fields = (
        'order_number',
        'date',
        'product_total',
        'subscription_total',
        'delivery_cost',
        'grand_total',
    )

    fields = (
        'order_number',
        'date',

        # User Information
        'full_name',
        'email',
        'phone_number',
        'country',
        'postcode',
        'town_or_city',
        'street_address1',
        'street_address2',
        'county',

        # Totals
        'product_total',
        'subscription_total',
        'delivery_cost',
        'grand_total',
    )

    list_display = (
        'order_number',
        'full_name',
        'email',
        'product_total',
        'subscription_total',
        'grand_total',
        'date',
    )

    ordering = ('-date',)
    