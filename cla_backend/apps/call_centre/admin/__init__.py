from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from core.admin.modeladmin import OneToOneUserAdmin
from .forms import OperatorAdminForm, FullOperatorAdminForm, CaseworkerAdminForm
from ..models import Operator, Caseworker, Organisation


class OperatorAdmin(OneToOneUserAdmin):
    actions = None
    simple_op_form = OperatorAdminForm
    full_op_form = FullOperatorAdminForm

    def operator_organisation(obj):
        return obj.organisation if obj.organisation else ""

    list_display = (
        "username_display",
        "email_display",
        "first_name_display",
        "last_name_display",
        "is_active_display",
        "is_manager",
        "is_cla_superuser",
        operator_organisation,
    )
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email"]
    list_filter = ["organisation__name"]

    def get_list_filter(self, request):
        return self.list_filter if self._is_loggedin_superuser(request) else []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organisation" and not self._is_loggedin_superuser(request):
            try:
                operator = request.user.operator
            except ObjectDoesNotExist:
                pass
            else:
                if operator.organisation:
                    kwargs["queryset"] = Organisation.objects.filter(pk=operator.organisation.id)
                    kwargs["required"] = True
                    kwargs["initial"] = operator.organisation.id
        return super(OperatorAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

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

    def get_queryset(self, request):
        qs = super(OperatorAdmin, self).get_queryset(request)
        if not self._is_loggedin_superuser(request):
            try:
                operator = request.user.operator
            except ObjectDoesNotExist:
                pass
            else:
                query = Q(organisation__isnull=True)
                query.add(Q(organisation=operator.organisation), Q.OR)
                qs = qs.filter(query)

        return qs

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


class CaseworkerAdmin(OneToOneUserAdmin):
    actions = None
    form = CaseworkerAdminForm
    list_display = (
        "username_display",
        "email_display",
        "first_name_display",
        "last_name_display",
        "is_active_display",
    )
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email"]

    def _is_loggedin_superuser(self, request):
        user = request.user
        if user.is_superuser:
            return True

        try:
            operator = user.operator
        except ObjectDoesNotExist:
            return False

        return operator.is_cla_superuser

    def has_change_permission(self, request, obj=None):
        """
        Rule:
        - django superuser can do everything
        - cla superusers can do everything
        """
        # if no permissions from standard django, don't even bother
        if not super(CaseworkerAdmin, self).has_change_permission(request, obj=obj):
            return False

        # if new user, go ahead
        if not obj or not obj.pk:
            return True

        # if logged-in user is django superuser or cla superuser do what you want
        if self._is_loggedin_superuser(request):
            return True

        if obj and request.user == obj.user:
            return True

        # anyone else can't do anything.

        return False


admin.site.register(Operator, OperatorAdmin)
admin.site.register(Caseworker, CaseworkerAdmin)
admin.site.register(Organisation)
