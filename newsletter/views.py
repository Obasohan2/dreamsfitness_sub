from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsletterSubscriber
from .utils import send_newsletter_confirmation


def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get("email")

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
                "You are already subscribed."
            )

        return redirect("newsletter")

    return render(request, "newsletter.html")