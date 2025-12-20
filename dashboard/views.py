from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from products.models import Product
from subscriptions.models import SubPlan, SubPlanFeature, PlanDiscount


@staff_member_required
def admin_dashboard(request):
    plans = SubPlan.objects.all()
    features = SubPlanFeature.objects.all()
    discounts = PlanDiscount.objects.all()
    products = Product.objects.all()

    context = {
        "plans": plans,
        "features": features,
        "discounts": discounts,
        "products": products,
    }

    return render(
        request, "dashboard/admin_dashboard.html", context
    )
