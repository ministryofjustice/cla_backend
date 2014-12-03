from core.admin.forms import OneToOneUserAdminForm

from ..models import Operator


class OperatorAdminForm(OneToOneUserAdminForm):
    class Meta:
        model = Operator
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'is_manager'
        ]
