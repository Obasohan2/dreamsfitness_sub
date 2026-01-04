from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
import logging

from .forms import ContactForm

logger = logging.getLogger(__name__)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            try:
                # ================= ADMIN EMAIL =================
                admin_html = render_to_string(
                    "emails/contact_admin.html",
                    data,
                )

                admin_email = EmailMultiAlternatives(
                    subject=f"New Contact Message: {data['subject']}",
                    body=data["message"],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                    reply_to=[data["email"]],
                )
                admin_email.attach_alternative(admin_html, "text/html")
                admin_email.send(fail_silently=False)

                # ================= USER CONFIRMATION EMAIL =================
                user_html = render_to_string(
                    "emails/contact_user.html",
                    data,
                )

                user_email = EmailMultiAlternatives(
                    subject="We received your message",
                    body="Thank you for contacting us.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[data["email"]],
                )
                user_email.attach_alternative(user_html, "text/html")
                user_email.send(fail_silently=False)

                messages.success(
                    request,
                    "Thank you for contacting us! We’ll get back to you soon."
                )
                return redirect("contact")

            except Exception:
                logger.error(
                    "Contact email failed",
                    exc_info=True,
                    extra={"email": data.get("email")},
                )
                messages.error(
                    request,
                    "Something went wrong sending your message. Please try again later."
                )

    else:
        form = ContactForm()

    return render(
        request,
        "contact/contact.html",
        {"form": form},
    )
