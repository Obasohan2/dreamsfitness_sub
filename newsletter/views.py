from django.http import JsonResponse
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .forms import NewsletterForm


def subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)

        if form.is_valid():
            try:
                subscriber = form.save()

                # Send email (non-blocking)
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

                return JsonResponse({
                    "status": "success",
                    "message": "Thanks for subscribing to our newsletter!"
                })

            except IntegrityError:
                return JsonResponse({
                    "status": "exists",
                    "message": "You’re already subscribed. Thanks for being with us!"
                })

        return JsonResponse({
            "status": "error",
            "message": "Please enter a valid email address."
        }, status=400)

    return JsonResponse({"status": "error"}, status=405)
