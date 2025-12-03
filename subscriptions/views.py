from django.shortcuts import render
from .models import SubPlan, SubPlanFeature


def pricing(request):
    plans = SubPlan.objects.order_by('price')
    dfeatures = SubPlanFeature.objects.all()
    
    return render(request, 'subscriptions/pricing.html', {
        'plans': plans,
        'dfeatures': dfeatures
    })
