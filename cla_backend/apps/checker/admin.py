from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib import admin, messages
from django.http.response import HttpResponseRedirect
from checker.models import ReasonForContacting, CallbackTimeSlot
from checker.forms import CallbackTimeSlotCSVUploadForm
import datetime


class ReasonForContactingAdmin(admin.ModelAdmin):
    list_display = ("created", "reason_categories", "case")
    date_hierarchy = "created"
    readonly_fields = ("reason_categories", "other_reasons", "case", "user_agent", "referrer")


class CallbackTimeSlotAdmin(admin.ModelAdmin):
    change_list_template = "admin/checker/callback-time-slots/custom_change_list.html"
    list_display = ("date", "time", "capacity", "remaining_capacity")
    date_hierarchy = "date"
    ordering = ("-date", "time")

    def get_urls(self):
        urls = super(CallbackTimeSlotAdmin, self).get_urls()
        my_urls = patterns(
            "",
            url(r"^import-csv/$", self.admin_site.admin_view(self.import_csv), name="callback_time_slots_import_csv"),
        )
        return my_urls + urls

    def import_csv(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        form = CallbackTimeSlotCSVUploadForm()
        if request.method == "POST":
            form = CallbackTimeSlotCSVUploadForm(files=request.FILES)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, "CSV Imported successfully")
                return HttpResponseRedirect(
                    reverse("admin:%s_%s_changelist" % (self.model._meta.app_label, self.model._meta.model_name))
                )
        return render(request, "admin/checker/callback-time-slots/csv-upload.html", {"form": form})

    def get_queryset(self, request):
        """ If there are no query arguments then only return a weeks worth of slots.
            This decreases the initial page load time by initially only loading the most relevant data

        Args:
            request (django.request)

        Returns:
            QuerySet: QuerySet of relevant callback time slots
        """
        if len(request.GET.items()) == 0:
            today = datetime.date.today()
            week_range = (today, today + datetime.timedelta(days=7))
            qs = CallbackTimeSlot.objects.filter(date__range=week_range)
            return qs
        qs = super(CallbackTimeSlotAdmin, self).get_queryset(request)

        return qs


admin.site.register(ReasonForContacting, ReasonForContactingAdmin)
admin.site.register(CallbackTimeSlot, CallbackTimeSlotAdmin)
