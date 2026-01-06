def newsletter_form(request):
    try:
        from newsletter.forms import NewsletterForm
        return {
            "newsletter_form": NewsletterForm()
        }
    except Exception:
        return {}



# def newsletter_success(request):
#     success = request.session.get("newsletter_success")

#     if success:
#         del request.session["newsletter_success"]

#     return {
#         "newsletter_success": success
#     }


