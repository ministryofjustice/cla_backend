from django.contrib import admin

from .models import Provider, ProviderAllocation, Staff


class StaffInline(admin.TabularInline):
    model = Staff


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
admin.site.register(Staff)
