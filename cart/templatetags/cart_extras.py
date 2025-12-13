from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter(name="mul")
def mul(value, arg):
    """
    Safely multiply two values (Decimal-safe).
    Intended for price × quantity.
    """
    try:
        return Decimal(value) * int(arg)
    except (TypeError, ValueError, InvalidOperation):
        return Decimal("0.00")
