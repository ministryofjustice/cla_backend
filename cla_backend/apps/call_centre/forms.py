from django import forms

from cla_provider.models import Provider

from legalaid.forms import OutcomeForm


class ProviderAllocationForm(OutcomeForm):
    provider = forms.ModelChoiceField(queryset=Provider.objects.active())

    def save(self, case, user):
        data = self.cleaned_data

        case.assign_to_provider(data['provider'])
        super(ProviderAllocationForm, self).save(case, user)


class UnlockCaseForm(OutcomeForm):
    pass
