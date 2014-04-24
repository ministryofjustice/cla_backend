from django import forms

from cla_provider.models import Provider


class ProviderAllocationForm(forms.Form):
    provider = forms.ModelChoiceField(queryset=Provider.objects.active())

    def save(self, case, user):
        data = self.cleaned_data

        case.assign_to_provider(data['provider'])
        return data['provider']


class CloseCaseForm(forms.Form):
    def save(self, case, user):
        case.close()
