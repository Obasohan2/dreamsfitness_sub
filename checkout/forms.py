from django import forms
from .models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            # Billing
            "full_name", "email", "phone_number",
            "address1", "address2", "city", "postcode", "country",

            # Shipping
            "shipping_full_name", "shipping_phone_number",
            "shipping_address1", "shipping_address2",
            "shipping_city", "shipping_postcode", "shipping_country",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            # Billing
            "full_name": "Full Name",
            "email": "Email Address",
            "phone_number": "Phone Number",
            "address1": "Billing Address Line 1",
            "address2": "Billing Address Line 2",
            "city": "Billing City",
            "postcode": "Billing Postcode",
            "country": "Billing Country",

            # Shipping
            "shipping_full_name": "Recipient Full Name",
            "shipping_phone_number": "Recipient Phone Number",
            "shipping_address1": "Shipping Address Line 1",
            "shipping_address2": "Shipping Address Line 2",
            "shipping_city": "Shipping City",
            "shipping_postcode": "Shipping Postcode",
            "shipping_country": "Shipping Country",
        }

        # Autofocus first field
        self.fields["full_name"].widget.attrs["autofocus"] = True

        #  MAKE SHIPPING FIELDS OPTIONAL (CRITICAL FIX)
        shipping_fields = [
            "shipping_full_name",
            "shipping_phone_number",
            "shipping_address1",
            "shipping_address2",
            "shipping_city",
            "shipping_postcode",
            "shipping_country",
        ]

        for field in shipping_fields:
            self.fields[field].required = False

        # Apply placeholders + styling
        for field in self.fields:
            if field not in ("country", "shipping_country"):
                ph = placeholders.get(field, "")
                placeholder = f"{ph} *" if self.fields[field].required else ph
                self.fields[field].widget.attrs["placeholder"] = placeholder

            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = False
