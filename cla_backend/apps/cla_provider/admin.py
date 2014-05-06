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

admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderAllocation)
admin.site.register(Staff)
