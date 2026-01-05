from django import forms
from django.core.validators import RegexValidator
from .models import Order


phone_validator = RegexValidator(
    regex=r'^\d{7,15}$',
    message='Enter a valid phone number (7–15 digits, numbers only).'
)


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

    # ================= STRICT FIELD OVERRIDES =================

    full_name = forms.CharField(
        min_length=3,
        max_length=100,
        required=True
    )

    email = forms.EmailField(required=True)

    phone_number = forms.CharField(
        validators=[phone_validator],
        required=True
    )

    shipping_phone_number = forms.CharField(
        validators=[phone_validator],
        required=False
    )

    postcode = forms.CharField(
        min_length=3,
        max_length=12,
        required=True
    )

    shipping_postcode = forms.CharField(
        min_length=3,
        max_length=12,
        required=False
    )

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

        self.fields["full_name"].widget.attrs["autofocus"] = True

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

        for field in self.fields:
            if field not in ("country", "shipping_country"):
                ph = placeholders.get(field, "")
                placeholder = f"{ph} *" if self.fields[field].required else ph
                self.fields[field].widget.attrs["placeholder"] = placeholder

            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = False

    # ================= CUSTOM CLEANING =================

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "")
        if not name.replace(" ", "").isalpha():
            raise forms.ValidationError(
                "Name must contain letters only."
            )
        return name

    def clean(self):
        """
        Require ALL shipping fields if ANY shipping field is filled
        """
        cleaned = super().clean()

        shipping_fields = [
            "shipping_full_name",
            "shipping_phone_number",
            "shipping_address1",
            "shipping_city",
            "shipping_postcode",
            "shipping_country",
        ]

        shipping_used = any(cleaned.get(field) for field in shipping_fields)

        if shipping_used:
            for field in shipping_fields:
                if not cleaned.get(field):
                    self.add_error(
                        field,
                        "This field is required for shipping."
                    )

        return cleaned
