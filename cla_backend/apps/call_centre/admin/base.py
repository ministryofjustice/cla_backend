from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from core.admin.modeladmin import OneToOneUserAdmin

from ..models import Operator

from .forms import OperatorAdminForm, FullOperatorAdminForm


class OperatorAdmin(OneToOneUserAdmin):
    actions = None
    simple_op_form = OperatorAdminForm
    full_op_form = FullOperatorAdminForm
    list_display = (
        'username_display', 'email_display',
        'first_name_display', 'last_name_display',
        'is_manager', 'is_cla_superuser'
    )

    def _is_loggedin_superuser(self, request):
        user = request.user
        if user.is_superuser:
            return True

        try:
            operator = user.operator
        except ObjectDoesNotExist:
            return False

        return operator.is_cla_superuser

    def get_form(self, request, obj=None, **kwargs):
        if self._is_loggedin_superuser(request):
            self.form = self.full_op_form
        else:
            self.form = self.simple_op_form

        return super(OperatorAdmin, self).get_form(request, obj=obj, **kwargs)

    def has_change_permission(self, request, obj=None):
        """
        Rule:
        - django superuser can do everything
        - operator manager can only change operators != cla superusers
        - cla superusers can do everything
        """
        # if no permissions from standard django, don't even bother
        if not super(OperatorAdmin, self).has_change_permission(request, obj=obj):
            return False

        # if new user, go ahead
        if not obj or not obj.pk:
            return True

        # if logged-in user is django superuser or cla superuser do what you want
        if self._is_loggedin_superuser(request):
            return True

        # at this point, logged-in user is operator manager or simple django staff
        # so he can only change the obj if the obj is not a cla superuser
        if obj.is_cla_superuser:
            return False

        return True

admin.site.register(Operator, OperatorAdmin)
