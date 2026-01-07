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
    """

    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            try:
                subscriber = form.save()

                # ✅ SUCCESS FLAG (this triggers modal)
                request.session["newsletter_success"] = "success"

            except IntegrityError:
                # ✅ ALREADY SUBSCRIBED FLAG
                request.session["newsletter_success"] = "exists"
                return redirect(request.META.get("HTTP_REFERER", "/"))

            # Send welcome email (non-blocking)
            try:
                website_url = request.build_absolute_uri("/")
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
                pass

    return redirect(request.META.get("HTTP_REFERER", "/"))