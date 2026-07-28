from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.utils.decorators import method_decorator
from django.utils.translation import gettext, gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import re_path

from cla_auth.models import AccessAttempt

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
require_POST_m = method_decorator(require_POST)


class OneToOneUserAdmin(admin.ModelAdmin):
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = None

    def has_view_permission(self, request, obj=None):
        return self.has_change_permission(request, obj=obj)

    def username_display(self, one2one_model):
        return one2one_model.user.username

    username_display.short_description = "Username"
    username_display.admin_order_field = "user__username"

    def first_name_display(self, one2one_model):
        return one2one_model.user.first_name

    first_name_display.short_description = "First name"
    first_name_display.admin_order_field = "user__first_name"

    def last_name_display(self, one2one_model):
        return one2one_model.user.last_name

    last_name_display.short_description = "Last name"
    last_name_display.admin_order_field = "user__last_name"

    def email_display(self, one2one_model):
        return one2one_model.user.email

    email_display.short_description = "Email"
    email_display.admin_order_field = "user__email"

    def is_active_display(self, one2one_model):
        return one2one_model.user.is_active

    is_active_display.short_description = "Is active"
    is_active_display.boolean = True
    is_active_display.admin_order_field = "user__is_active"

    def save_model(self, request, obj, form, change):
        user = obj.user

        # Keep user fields synchronized even if admin form/model save flow changes.
        if hasattr(form, "get_user_fields"):
            for field in form.get_user_fields():
                if field in form.cleaned_data:
                    setattr(user, field, form.cleaned_data[field])

        user.save()

        obj.user = user
        obj.save()

    def get_urls(self):
        urls = [
            re_path(r"^(\d+)/change/password/$", self.admin_site.admin_view(self.user_change_password)),
            re_path(r"^(\d+)/password/$", self.admin_site.admin_view(self.user_change_password)),
            re_path(r"^(\d+)/change/reset-lockout/$", self.admin_site.admin_view(self.reset_lockout)),
            re_path(r"^(\d+)/reset-lockout/$", self.admin_site.admin_view(self.reset_lockout)),
        ]
        return urls + super(OneToOneUserAdmin, self).get_urls()

    @require_POST_m
    def reset_lockout(self, request, id):
        one2one_model = get_object_or_404(self.get_queryset(request), pk=id)
        if not self.has_change_permission(request, one2one_model):
            raise PermissionDenied

        user = one2one_model.user

        AccessAttempt.objects.delete_for_username(user.username)

        self.log_change(request, user, "Reset locked account (user %s)" % user.username)
        msg = gettext("Account unlocked successfully.")
        messages.success(request, msg)
        return HttpResponseRedirect("..")

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=""):
        one2one_model = get_object_or_404(self.get_queryset(request), pk=id)
        if not self.has_change_permission(request):
            raise PermissionDenied

        user = one2one_model.user
        if request.method == "POST":
            if not self.has_change_permission(request, one2one_model):
                raise PermissionDenied
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = gettext("Password changed successfully.")
                messages.success(request, msg)
                return HttpResponseRedirect("..")
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {"fields": list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            "title": _("Change password: %s") % escape(user.get_username()),
            "adminForm": adminForm,
            "form_url": form_url,
            "form": form,
            "is_popup": IS_POPUP_VAR in request.GET,
            "add": True,
            "change": False,
            "has_delete_permission": False,
            "has_change_permission": True,
            "has_absolute_url": False,
            "opts": self.model._meta,
            "original": one2one_model,
            "save_as": False,
            "show_save": True,
        }
        return TemplateResponse(
            request,
            self.change_user_password_template or "admin/auth/user/change_password.html",
            context,
        )
