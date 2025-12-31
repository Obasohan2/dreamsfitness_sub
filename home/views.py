from django.shortcuts import render

# Create your views here.


def index(request):
    """View function for home page of site."""
    return render(request, 'home/index.html')


def terms(request):
    return render(request, "terms.html")


def nutrition_guides(request):
    return render(request, "nutrition_guides.html")




