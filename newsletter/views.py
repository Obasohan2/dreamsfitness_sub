from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsletterSubscriber
from .utils import send_newsletter_confirmation


def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Please enter a valid email address.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={"consent": True}
        )

        if created:
            send_newsletter_confirmation(email)
            messages.success(
                request,
                "You’ve successfully subscribed to our newsletter!",
                extra_tags="newsletter"
            )
        else:
            messages.info(
                request,
                "You are already subscribed.",
                extra_tags="newsletter"
            )

        return redirect(request.META.get("HTTP_REFERER", "/"))

    return redirect("/")
