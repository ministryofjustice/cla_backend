# -*- coding: utf-8 -*-
import datetime
from django.contrib import admin

from .models import Notification


def set_end_time_in_past(modeladmin, request, queryset):
    queryset.update(end_time=datetime.datetime.now())
set_end_time_in_past.short_description = "Set end time in the past to " \
                                         "remove notification"


class NotificationAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'description', 'type')
    list_display = (
        'id',
        'notification',
        'type',
        'start_time',
        'end_time',
    )
    actions = (set_end_time_in_past,)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.save()


admin.site.register(Notification, NotificationAdmin)