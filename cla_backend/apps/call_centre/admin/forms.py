from core.admin.forms import OneToOneUserAdminForm

from ..models import Operator


class OperatorAdminForm(OneToOneUserAdminForm):
    class Meta:
        model = Operator
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'is_manager'
        ]


class FullOperatorAdminForm(OneToOneUserAdminForm):
    """
    Like OperatorAdminForm but with 'is_cla_superuser' added.
    """
    class Meta:
        model = Operator
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'is_manager', 'is_cla_superuser'
        ]
