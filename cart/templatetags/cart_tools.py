from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


@register.filter(name="calc_subtotal")
def calc_subtotal(price, quantity):
    """
    Safely calculate subtotal = price × quantity
    Handles Decimal, int, str, and invalid values.
    """
    try:
        price = Decimal(price)
        quantity = int(quantity)
        return price * quantity
    except (TypeError, ValueError, InvalidOperation):
        return Decimal("0.00")
