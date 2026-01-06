def newsletter_success(request):
    """
    Makes newsletter success message available once,
    then removes it from the session.
    """

    success = request.session.get("newsletter_success")

    if success:
        del request.session["newsletter_success"]

    return {
        "newsletter_success": success
    }
