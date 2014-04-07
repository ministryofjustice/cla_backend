from django import forms
from cla_provider.models import Provider


class ProviderAllocationForm(forms.Form):
    provider = forms.ModelChoiceField(queryset=Provider.objects.active())

