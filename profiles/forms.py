from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    User profile update form (no image upload)
    """

    class Meta:
        model = UserProfile
        fields = (
            "default_phone_number",
            "default_street_address1",
            "default_street_address2",
            "default_town_or_city",
            "default_postcode",
            "default_country",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "default_phone_number": "Phone Number",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_town_or_city": "Town or City",
            "default_postcode": "Postal Code",
            "default_country": "Country",
        }

        # Autofocus first field
        self.fields["default_phone_number"].widget.attrs["autofocus"] = True

        for name, field in self.fields.items():
            placeholder = placeholders.get(name, "")
            if field.required:
                placeholder += " *"

            field.widget.attrs.update({
                "placeholder": placeholder,
                "class": "form-control border-black rounded-0 profile-form-input",
            })

            # Hide labels for clean UI
            field.label = False
