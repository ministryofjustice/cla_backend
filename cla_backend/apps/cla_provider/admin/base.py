from django.contrib import admin

from core.admin.modeladmin import OneToOneUserAdmin

from ..models import Provider, ProviderAllocation, Staff, OutOfHoursRota

from .forms import StaffAdminForm


class StaffAdmin(OneToOneUserAdmin):
    model = Staff
    form = StaffAdminForm

    actions = None
    list_display = (
        'username_display', 'email_display',
        'first_name_display', 'last_name_display',
        'provider', 'is_active_display', 'is_manager'
    )
    search_fields = [
        'user__username',
        'user__first_name', 'user__last_name', 'user__email'
    ]


class ProviderAllocationInline(admin.TabularInline):
    model = ProviderAllocation


class ProviderAdmin(admin.ModelAdmin):
    actions = None
    inlines = [ProviderAllocationInline]

    fields = (
        'name', 'short_code', 'telephone_frontdoor', 'telephone_backdoor',
        'email_address', 'active'
    )
    list_display = ['name', 'law_categories', 'active']

    def law_categories(self, obj):
        return u', '.join(
            obj.providerallocation_set.values_list('category__code', flat=True)
        )


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderAllocation)
admin.site.register(OutOfHoursRota)
admin.site.register(Staff, StaffAdmin)
