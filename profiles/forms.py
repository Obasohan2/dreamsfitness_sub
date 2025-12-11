from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        """Add placeholders, classes, remove labels, set autofocus."""
        super().__init__(*args, **kwargs)

        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_country': 'Country',
        }

        # Autofocus on first field
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        for field in self.fields:
            if field != 'default_country':  # Country field has a select dropdown
                placeholder = placeholders.get(field, '')
                if self.fields[field].required:
                    placeholder += ' *'
                self.fields[field].widget.attrs['placeholder'] = placeholder

            self.fields[field].widget.attrs['class'] = (
                'form-control border-black rounded-0 profile-form-input'
            )

            # Remove labels (crispy will handle layout)
            self.fields[field].label = False
