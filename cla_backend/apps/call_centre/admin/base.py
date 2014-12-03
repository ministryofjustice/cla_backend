from django.contrib import admin
from django.contrib.admin.options import IS_POPUP_VAR
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm

from ..models import Operator

from .forms import OperatorAdminForm

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class OperatorAdmin(admin.ModelAdmin):
    form = OperatorAdminForm
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_manager'
    )
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = None

    def username(self, op):
        return op.user.username

    def first_name(self, op):
        return op.user.first_name

    def last_name(self, op):
        return op.user.last_name

    def email(self, op):
        return op.user.email

    def is_manager(self, op):
        return op.user.is_manager

    def save_model(self, request, obj, form, change):
        user = obj.user
        user.save()

        obj.user = user
        obj.save()

    def get_urls(self):
        from django.conf.urls import patterns
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(self.user_change_password))
        ) + super(OperatorAdmin, self).get_urls()

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        operator = get_object_or_404(self.get_queryset(request), pk=id)
        user = operator.user
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': IS_POPUP_VAR in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': operator,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context, current_app=self.admin_site.name)

admin.site.register(Operator, OperatorAdmin)
