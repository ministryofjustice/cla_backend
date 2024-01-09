from django.contrib import admin
import nested_admin

import logging

from core.admin.modeladmin import OneToOneUserAdmin
from django.contrib.admin.options import InlineModelAdmin

from ..models import Provider, ProviderAllocation, Staff, OutOfHoursRota, WorkingDays

from .forms import StaffAdminForm
from .formsets import ProviderAllocationInlineFormset, WorkingDaysInlineFormset


class StaffAdmin(OneToOneUserAdmin):
    model = Staff
    form = StaffAdminForm

    actions = None
    list_display = (
        "username_display",
        "email_display",
        "first_name_display",
        "last_name_display",
        "provider",
        "is_active_display",
        "is_manager",
    )
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email"]
 

class WorkingDaysInline(admin.TabularInline):
    model = WorkingDays
    formset = WorkingDaysInlineFormset
    template = 'admin/cla_provider/allocations/working_days_tabular_inline.html'


class ProviderAllocationInline(nested_admin.NestedTabularInline):
    model = ProviderAllocation
    formset = ProviderAllocationInlineFormset
    inlines = [WorkingDaysInline]
    template = 'admin/cla_provider/allocations/provider_allocation_tabular_inline.html'
        


class ProviderAdmin(nested_admin.NestedModelAdmin):
    actions = None
    inlines = [ProviderAllocationInline]

    fields = ("name", "short_code", "telephone_frontdoor", "telephone_backdoor", "email_address", "active")
    list_display = ["name", "law_categories", "active"]

    def law_categories(self, obj):
        return u", ".join(obj.providerallocation_set.values_list("category__code", flat=True))


admin.site.register(Provider, ProviderAdmin)
admin.site.register(OutOfHoursRota)
admin.site.register(Staff, StaffAdmin)
