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

    is_active = forms.BooleanField(required=False, initial=True)

    def get_defaults(self):
        defaults = super(CaseworkerAdminForm, self).get_defaults()
        defaults.update({'is_staff': True})
        return defaults

    class Meta:
        model = Caseworker
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'is_active',
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
