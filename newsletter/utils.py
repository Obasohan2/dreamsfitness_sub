from django.core.mail import send_mail
from django.conf import settings


def send_newsletter_confirmation(email):
    subject = "Welcome to Dreams Fitness 💪"
    message = (
        "Thank you for subscribing to the Dreams Fitness newsletter!\n\n"
        "You’ll receive exclusive fitness tips, nutrition advice, and special offers.\n\n"
        "Stay strong,\n"
        "Dreams Fitness Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
