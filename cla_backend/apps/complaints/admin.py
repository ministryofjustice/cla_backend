# coding=utf-8
from django.contrib import admin

from .models import Category, Complaint


class ComplaintAdmin(admin.ModelAdmin):
    raw_id_fields = ["eod"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.save()

    # Shouldn't be editable
    exclude = ("audit_log",)


admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Category)
