from cla_provider.forms import AdminStaffForm
from django.contrib import admin

from .models import Provider, ProviderAllocation, Staff, OutOfHoursRota


class StaffInline(admin.TabularInline):
    model = Staff
    form = AdminStaffForm

class StaffAdmin(admin.ModelAdmin):
    model = Staff
    form = AdminStaffForm


class ProviderAllocationInline(admin.TabularInline):
    model = ProviderAllocation


class ProviderAdmin(admin.ModelAdmin):
    inlines = [
        ProviderAllocationInline,
        StaffInline,
    ]

    list_display = ['name', 'law_categories']

    def law_categories(self, obj):
        return u', '.join(
            obj.providerallocation_set.values_list('category__code', flat=True)
        )


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderAllocation)
admin.site.register(OutOfHoursRota)
admin.site.register(Staff, StaffAdmin)
