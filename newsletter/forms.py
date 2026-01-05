from django import forms
from .models import NewsletterSubscriber


class NewsletterForm(forms.ModelForm):

    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "consent"]

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Your email",
            "class": "form-control form-control-sm",
            "required": True,
        })
    )

    consent = forms.BooleanField(
        required=True,
        label="I agree to receive emails from Dreams Fitness Center and accept the"
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if NewsletterSubscriber.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already subscribed."
            )
        return email
