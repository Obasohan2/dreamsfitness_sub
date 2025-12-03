from django.contrib import admin
from . import models


@admin.register(models.SubPlan)
class SubPlanAdmin(admin.ModelAdmin):
    list_editable = ('highlight_status', 'max_member')
    list_display = ('title', 'price', 'max_member', 'validity_days', 'highlight_status')


@admin.register(models.SubPlanFeature)
class SubPlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_subplans')

    def display_subplans(self, obj):
        return " | ".join([sub.title for sub in obj.subplan.all()])
    display_subplans.short_description = "Sub Plans"


@admin.register(models.PlanDiscount)
class PlanDiscountAdmin(admin.ModelAdmin):
    list_display = ('subplan', 'total_months', 'total_discount')