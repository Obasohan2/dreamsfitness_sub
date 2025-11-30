from decimal import Decimal
from django import template

register = template.Library()

@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    """Return subtotal = price × quantity with proper Decimal handling."""
    try:
        return Decimal(price) * int(quantity)
    except (ValueError, TypeError):
        return Decimal('0.00')
