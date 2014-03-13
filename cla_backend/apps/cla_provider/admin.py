from django.contrib import admin
from .models import Provider, Staff

class StaffInline(admin.TabularInline):
    model = Staff

class ProviderAdmin(admin.ModelAdmin):
    inlines = [
        StaffInline,
        ]

admin.site.register(Provider, ProviderAdmin)
admin.site.register(Staff)
