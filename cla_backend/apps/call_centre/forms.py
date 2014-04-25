from django import forms

from cla_provider.models import Provider


class ProviderAllocationForm(forms.Form):
    provider = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        self.providers = kwargs.pop('providers', None)
        if self.providers:
            self.base_fields['provider'].choices = [(p.pk, p.name) for p in self.providers]
        super(ProviderAllocationForm, self).__init__(*args, **kwargs)

    def clean_provider(self):
        provider = self.cleaned_data['provider']

        provider_obj = Provider.objects.get(pk=provider)
        self.cleaned_data['provider_obj'] = provider_obj
        return provider

    def save(self, case, user):
        data = self.cleaned_data

        case.assign_to_provider(data['provider_obj'])
        return data['provider_obj']


class CloseCaseForm(forms.Form):
    def save(self, case, user):
        case.close()
