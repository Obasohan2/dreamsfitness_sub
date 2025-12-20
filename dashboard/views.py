from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from products.models import Product
from subscriptions.models import SubPlan, Subscription


@staff_member_required
def admin_dashboard(request):
    """ Admin dashboard: products + subscriptions """

    products = Product.objects.all()
    plans = SubPlan.objects.all()
    subscriptions = Subscription.objects.all()

    context = {
        "products": products,
        "plans": plans,
        "subscriptions": subscriptions,
    }

    return render(request, "dashboard/admin_dashboard.html", context)
