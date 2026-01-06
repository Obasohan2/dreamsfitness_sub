def newsletter_success(request):
    success = request.session.get("newsletter_success")

    if success:
        del request.session["newsletter_success"]

    return {
        "newsletter_success": success
    }
