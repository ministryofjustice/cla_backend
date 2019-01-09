from django.contrib import admin
from checker.models import ReasonForContacting


class ReasonForContactingAdmin(admin.ModelAdmin):
    list_display = ("created", "reason_categories", "case")
    date_hierarchy = "created"
    readonly_fields = ("reason_categories", "other_reasons", "case", "user_agent", "referrer")


admin.site.register(ReasonForContacting, ReasonForContactingAdmin)
