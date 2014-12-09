from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.admin import widgets
from django.forms import PasswordInput

from core.admin.forms import OneToOneUserAdminForm

from ..models import Staff


class StaffAdminForm(OneToOneUserAdminForm):
    chs_password = ReadOnlyPasswordHashField(
        widget=PasswordInput(attrs={'class': 'vTextField'}), required=False,
        help_text='Password can only be set, not viewed.'
    )
    chs_organisation = forms.CharField(
        initial=None, required=False,
        widget=widgets.AdminTextInputWidget
    )
    chs_user = forms.CharField(
        initial=None, required=False,
        widget=widgets.AdminTextInputWidget
    )

    def clean(self):
        data = self.cleaned_data
        if not data['chs_password']:
            del self.cleaned_data['chs_password']
        return data

    def save(self, commit=True):
        raw_password = self.cleaned_data.get('chs_password')
        if raw_password:
            self.instance.set_chs_password(raw_password)
        return super(StaffAdminForm, self).save(commit=commit)

    class Meta:
        model = Staff
        fields = [
            'username', 'password', 'password2', 'first_name',
            'last_name', 'email', 'provider',
            'chs_organisation', 'chs_user', 'chs_password',
            'is_active', 'is_manager'
        ]
