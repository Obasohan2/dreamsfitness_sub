from .forms import NewsletterForm


def newsletter_success(request):
    success = request.session.get("newsletter_success")

    if success:
        # Remove it immediately so it only shows once
        del request.session["newsletter_success"]

    return {
        "newsletter_success": success
    }
