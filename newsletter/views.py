from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def subscribe(request):
    """
    Handle newsletter subscription via AJAX.

    Expects:
    - email (POST)
    - consent (POST)

    Returns:
    - JSON success response for frontend modal
    """

    email = (request.POST.get("email") or "").strip()
    consent = request.POST.get("consent")

    # Basic validation
    if not email:
        return JsonResponse(
            {"success": False, "message": "Email is required."},
            status=400
        )

    if not consent:
        return JsonResponse(
            {"success": False, "message": "Consent is required."},
            status=400
        )

    # ----------------------------------
    # TODO (optional, later):
    # - Save email to database
    # - Send to Mailchimp / SendGrid
    # - Prevent duplicates
    # ----------------------------------

    return JsonResponse(
        {
            "success": True,
            "message": "Subscription successful!"
        },
        status=200
    )
