from django.contrib import admin
from django.contrib.admin.exceptions import AlreadyRegistered
import nested_admin

from cla_provider.models import Provider, ProviderAllocation, Staff, OutOfHoursRota, WorkingDays
from core.admin.modeladmin import OneToOneUserAdmin

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
    template = "admin/cla_provider/allocations/working_days_tabular_inline.html"


class ProviderAllocationInline(nested_admin.NestedTabularInline):
    model = ProviderAllocation
    formset = ProviderAllocationInlineFormset
    inlines = [WorkingDaysInline]
    template = "admin/cla_provider/allocations/provider_allocation_tabular_inline.html"


class ProviderAdmin(nested_admin.NestedModelAdmin):
    actions = None
    inlines = [ProviderAllocationInline]

    fields = ("name", "short_code", "telephone_frontdoor", "telephone_backdoor", "email_address", "active")
    list_display = ["name", "law_categories", "active"]

    def law_categories(self, obj):
        return u", ".join(obj.providerallocation_set.values_list("category__code", flat=True))


for model, admin_class in (
    (Provider, ProviderAdmin),
    (OutOfHoursRota, None),
    (Staff, StaffAdmin),
):
    try:
        if admin_class is None:
            admin.site.register(model)
        else:
            admin.site.register(model, admin_class)
    except AlreadyRegistered:
        pass
