from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _


class OneToOneUserAdminForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(
        label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})

    # password fields are actually set dynamically depending on if we're creating or
    # updating an operator. The values in PASSWORD_FIELDS are used instead.
    password = forms.CharField(label=_("Password"))
    password2 = forms.CharField(label=_("Password confirmation"))
    PASSWORD_FIELDS = {
        'CREATE': {
            'password': forms.CharField(
                label=_("Password"),
                widget=forms.PasswordInput),
            'password2': forms.CharField(
                label=_("Password confirmation"),
                widget=forms.PasswordInput,
                help_text=_("Enter the same password as above, for verification."))
        },

        'UPDATE': {
            'password': ReadOnlyPasswordHashField(
                label=_("Password"),
                help_text=_("Raw passwords are not stored, so there is no way to see "
                            "this user's password, but you can change the password "
                            "using <a href=\"password/\">this form</a>.")
            ),
            'password2': ReadOnlyPasswordHashField(label=_("Password confirmation")),
        }
    }

    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    def adjust_password_fields(self, instance):
        for field_name in ['password', 'password2']:
            action = 'CREATE' if not instance else 'UPDATE'
            self.base_fields[field_name] = self.PASSWORD_FIELDS[action][field_name]

    def adjust_username_field(self, instance):
        attrs = self.base_fields['username'].widget.attrs
        if instance:
            attrs['readonly'] = True
        else:
            if 'readonly' in attrs:
                del attrs['readonly']

    def adjust_initial(self, instance, initial):
        initial['username'] = instance.user.username
        initial['first_name'] = instance.user.first_name
        initial['last_name'] = instance.user.last_name
        initial['email'] = instance.user.email
        initial['password'] = instance.user.password
        initial['password2'] = instance.user.password

        return initial

    def __init__(self, data=None, files=None, **kwargs):
        instance = kwargs.get('instance')

        self.adjust_password_fields(instance)
        self.adjust_username_field(instance)
        if instance:
            initial = kwargs.get('initial', {})
            kwargs['initial'] = self.adjust_initial(instance, initial)

        super(OneToOneUserAdminForm, self).__init__(
            data=data, files=files, **kwargs
        )

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)

        if qs.count():
            raise forms.ValidationError(self.error_messages['duplicate_username'])

        return username

    def clean_password2(self):
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]

        if not self.instance.pk and password != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def clean_password(self):
        if self.instance.pk:
            return self.initial["password"]
        return self.cleaned_data['password']

    def save(self, commit=True):
        onetoone_model = super(OneToOneUserAdminForm, self).save(commit=False)

        if not self.instance.pk:
            onetoone_model.user = User()

        onetoone_model.user.username = self.cleaned_data['username']
        onetoone_model.user.first_name = self.cleaned_data['first_name']
        onetoone_model.user.last_name = self.cleaned_data['last_name']
        onetoone_model.user.email = self.cleaned_data['email']

        if not self.instance.pk:
            onetoone_model.user.set_password(self.cleaned_data["password"])

        if commit:
            onetoone_model.user.save()
            onetoone_model.save()
        return onetoone_model
