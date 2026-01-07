from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def subscribe(request):
    email = request.POST.get("email")

    # TODO: save email / validate / send to provider

    return JsonResponse({"success": True})
