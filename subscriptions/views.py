from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from .models import SubPlan, SubPlanFeature


from django.shortcuts import render
from django.db.models import Count
from .models import SubPlan, SubPlanFeature


def pricing(request):
    plans = (
        SubPlan.objects
        .annotate(total_members=Count('subscriptionlineitem'))
        .order_by('price')
    )

    dfeatures = SubPlanFeature.objects.all()

    return render(request, 'subscriptions/pricing.html', {
        "plans": plans,
        "dfeatures": dfeatures,
    })

# def sub_checkout(request, plan_id):
#     planDetail = get_object_or_404(SubPlan, pk=plan_id)
#     return render(request, 'subscriptions/sub_checkout.html', {'plan': planDetail})


def sub_checkout(request, plan_id):
    plan = get_object_or_404(SubPlan, pk=plan_id)

    # Registered members
    registered = plan.subscriptionlineitem_set.count()

    # Balance seats
    balance = plan.max_member - registered

    # CORRECT ManyToMany reverse accessor
    features = plan.subplanfeature_set.all()

    # CORRECT because you used related_name="discounts"
    discounts = plan.discounts.all()

    return render(request, "subscriptions/sub_checkout.html", {
        "plan": plan,
        "registered": registered,
        "balance": balance,
        "features": features,
        "discounts": discounts,
    })



