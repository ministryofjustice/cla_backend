from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _

from cla_provider.models import Provider
from django.forms.util import ErrorList
from legalaid.forms import BaseCaseLogForm


class ProviderAllocationForm(BaseCaseLogForm):

    CASELOGTYPE_CODE = 'REFSP'

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

    def clean(self):
        cleaned_data = super(ProviderAllocationForm,self).clean()
        if not self.providers:
            self._errors[NON_FIELD_ERRORS] = ErrorList([
                _(u'There is no provider specified in '
                  u'the system to handle cases of this law category.')
            ])
            del self._errors['provider']
        return cleaned_data

    def get_notes(self):
        return u"Assigned to {provider}".format(provider=self.cleaned_data['provider_obj'].name)

    def save(self, case, user):
        data = self.cleaned_data

        case.assign_to_provider(data['provider_obj'])

        super(ProviderAllocationForm, self).save(case, user)
        return data['provider_obj']


class CloseCaseForm(forms.Form):
    def save(self, case, user):
        case.close()
