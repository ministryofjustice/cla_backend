from core.admin.forms import OneToOneUserAdminForm
from django import forms

from ..models import Operator, Caseworker


class OperatorAdminForm(OneToOneUserAdminForm):
    class Meta:
        model = Operator
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'is_active', 'is_manager'
        ]

class CaseworkerAdminForm(OneToOneUserAdminForm):

    is_staff = forms.BooleanField(required=False, initial=True)
    is_active = forms.BooleanField(required=False, initial=True)

    def adjust_initial(self, instance, initial):
        initial = super(CaseworkerAdminForm, self).adjust_initial(instance, initial)
        initial['is_staff'] = instance.user.is_staff
        return initial

    def get_user_fields(self):
        return super(CaseworkerAdminForm, self).get_user_fields() + ['is_staff']

    class Meta:
        model = Caseworker
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'is_active', 'is_staff'
        ]




class FullOperatorAdminForm(OneToOneUserAdminForm):
    """
    Like OperatorAdminForm but with 'is_cla_superuser' added.
    """
    class Meta:
        model = Operator
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email',
            'is_active', 'is_manager', 'is_cla_superuser'
        ]
