from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import IntegrityError

from .forms import NewsletterForm


def subscribe(request):
    """
    Handle newsletter subscriptions safely.
    - Validates input via NewsletterForm
    - Saves subscriber
    - Sends welcome email (fails silently)
    - Sets success flag in session
    """

    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            try:
                subscriber = form.save(commit=True)

            except IntegrityError:
                # Email already exists → treat as success, no crash
                request.session["newsletter_success"] = True
                return redirect(request.META.get("HTTP_REFERER", "/"))

            website_url = request.build_absolute_uri("/")

            try:
                html_message = render_to_string(
                    "emails/newsletter_welcome.html",
                    {"website_url": website_url},
                )
                plain_message = strip_tags(html_message)

                email = EmailMultiAlternatives(
                    subject="Welcome to Dreams Fitness Center",
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email],
                )
                email.attach_alternative(html_message, "text/html")
                email.send(fail_silently=True)

            except Exception:
                # Email failure should never block signup
                pass

            request.session["newsletter_success"] = True

    return redirect(request.META.get("HTTP_REFERER", "/"))
