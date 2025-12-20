from django.http import HttpResponse

# Create your views here.


def blog_home(request):
    return HttpResponse("Blog home page")
