from django.contrib import admin

from core.admin.modeladmin import OneToOneUserAdmin

from ..models import Operator

from .forms import OperatorAdminForm


class OperatorAdmin(OneToOneUserAdmin):
    form = OperatorAdminForm
    list_display = (
        'username_display', 'email_display',
        'first_name_display', 'last_name_display', 'is_manager'
    )

admin.site.register(Operator, OperatorAdmin)
