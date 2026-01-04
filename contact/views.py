from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render, redirect

from .forms import ContactForm


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            try:
                # Admin email
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
                admin_email.send(fail_silently=True)

                # User confirmation email
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
                user_email.send(fail_silently=True)

            except Exception:
                # Do NOT crash the site
                pass

            messages.success(
                request,
                "Thanks for contacting us — your message has been sent!"
            )
            return redirect("contact")

    else:
        form = ContactForm()

    return render(
        request,
        "contact/contact.html",
        {"form": form},
    )
