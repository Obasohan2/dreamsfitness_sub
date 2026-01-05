from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import NewsletterForm


def subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subscriber = form.save()

            website_url = request.build_absolute_uri("/")

            html_message = render_to_string(
                "newsletter/newsletter.html",
                {"website_url": website_url}
            )
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject="Welcome to Dreams Fitness Center",
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

    return redirect(request.META.get("HTTP_REFERER", "/"))
