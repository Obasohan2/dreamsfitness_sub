from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "full_name", "email", "phone_number",
            "address1", "address2", "city", "postcode", "country"
        ]
