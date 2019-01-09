# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


AUTOCOMPLETE_OFF_ATTRS = {"autocomplete": "off", "readonly": True, "onfocus": 'this.removeAttribute("readonly");'}


class CLALoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs=AUTOCOMPLETE_OFF_ATTRS))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs=AUTOCOMPLETE_OFF_ATTRS))
