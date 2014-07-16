from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

from cla_provider.models import Provider
from cla_eventlog.forms import BaseCaseLogForm, EventSpecificLogForm


class ProviderAllocationForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'assign_to_provider'

    provider = forms.ChoiceField()
    is_manual = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.providers = kwargs.pop('providers', None)
        if self.providers:
            self.base_fields['provider'].choices = [(p.pk, p.name) for p in
                                                    self.providers]
        super(ProviderAllocationForm, self).__init__(*args, **kwargs)

    def clean_provider(self):
        provider = self.cleaned_data['provider']

        provider_obj = Provider.objects.get(pk=provider)
        self.cleaned_data['provider_obj'] = provider_obj
        return provider

    def clean(self):
        cleaned_data = super(ProviderAllocationForm, self).clean()
        nfe = []
        if not self.providers:
            nfe.append(
                _(u'There is no provider specified in '
                  u'the system to handle cases of this law category.')
            )
            del self._errors['provider']

        if not (self.case.matter_type1 and self.case.matter_type2):
            nfe.append(_(u"Can't assign to specialist provider without setting "
                         u"matter_type1 and matter_type2"))

        if (self.case.matter_type1 and self.case.matter_type2) and (
                not self.case.matter_type1.category == self.case.matter_type2.category):
            nfe.append(_(
                u"Category of matter type 1: {} must match category of matter type 2: {}".format(
                    self.case.matter_type1.category.name,
                    self.case.matter_type2.category)))

        if self.case.eligibility_check:
            case_category = self.case.eligibility_check.category
            mt1_category = self.case.matter_type1.category if self.case.matter_type1 else None
            mt2_category = self.case.matter_type2.category if self.case.matter_type2 else None
            if (case_category and mt1_category and mt2_category):
                if (case_category != mt1_category or case_category != mt2_category):
                    nfe.append(_(
                        u"Category of Matter Types: {},{} must match category of case: {}".format(
                            mt1_category.name, mt2_category.name,
                            case_category.name)))

        if nfe:
            self._errors[NON_FIELD_ERRORS] = ErrorList(nfe)
        return cleaned_data

    def get_notes(self):
        notes = self.cleaned_data['notes']
        if not notes and not self.get_is_manual():
            notes = u"Assigned to {provider}".format(
                provider=self.cleaned_data['provider_obj'].name)
        return notes

    def get_is_manual(self):
        return self.cleaned_data['is_manual']

    def get_kwargs(self):
        kwargs = super(ProviderAllocationForm, self).get_kwargs()
        kwargs['is_manual'] = self.get_is_manual()
        return kwargs

    def save(self, user):
        data = self.cleaned_data

        self.case.assign_to_provider(data['provider_obj'])

        super(ProviderAllocationForm, self).save(user)
        return data['provider_obj']


class DeferAssignmentCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'defer_assignment'


class DeclineAllSpecialistsCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'decline_help'


class SuspendCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'suspend_case'
