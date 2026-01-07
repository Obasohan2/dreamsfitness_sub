from django.core.mail import send_mail
from django.conf import settings


def send_newsletter_confirmation(email):
    subject = "Subscription Confirmed 🎉"
    message = (
        "Thanks for subscribing to our newsletter!\n\n"
        "You’ll now receive updates, offers, and news straight to your inbox.\n\n"
        "If this wasn’t you, you can unsubscribe anytime."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
