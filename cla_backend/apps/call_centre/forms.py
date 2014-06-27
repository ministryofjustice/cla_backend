from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList

from cla_common.constants import CASELOGTYPE_ACTION_KEYS

from cla_provider.models import Provider
from legalaid.forms import BaseCaseLogForm, OutcomeForm


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

    def save(self, user):
        data = self.cleaned_data

        self.case.assign_to_provider(data['provider_obj'])

        super(ProviderAllocationForm, self).save(user)
        return data['provider_obj']


class AssociatePersonalDetailsCaseForm(forms.Form):
    reference = forms.CharField(required=True, max_length=32)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(AssociatePersonalDetailsCaseForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.case.personal_details:
            raise ValidationError(u'There is already a person associated to this case.')
        return self.cleaned_data

    def save(self, user):
        ref = self.cleaned_data['reference']
        self.case.associate_personal_details(ref)


class AssociateEligibilityCheckCaseForm(forms.Form):
    reference = forms.CharField(required=True, max_length=32)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(AssociateEligibilityCheckCaseForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.case.eligibility_check:
            raise ValidationError(u'There is already an eligibility check associated to this case.')
        return self.cleaned_data

    def save(self, user):
        ref = self.cleaned_data['reference']
        self.case.associate_eligibility_check(ref)


class CloseCaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(CloseCaseForm, self).__init__(*args, **kwargs)

    def save(self, user):
        self.case.close()


class CaseAssignDeferForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'defer_assignment'

    def clean(self):
        cleaned_data = super(CaseAssignDeferForm, self).clean()
        if self._errors:  # skip if already in error
            return cleaned_data

        # checking that the case is in a consistent state
        if self.case.provider:
            self._errors[NON_FIELD_ERRORS] = ErrorList(['Case currently assigned to a provider'])
        return cleaned_data


class DeclineAllSpecialistsCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(DeclineAllSpecialistsCaseForm, self).get_outcome_code_queryset()
        return qs.filter(action_key=CASELOGTYPE_ACTION_KEYS.DECLINE_SPECIALISTS)

    def clean(self):
        cleaned_data = super(DeclineAllSpecialistsCaseForm, self).clean()
        if self._errors:  # skip if already in error
            return cleaned_data

        # checking that the case is in a consistent state
        if self.case.provider:
            self._errors[NON_FIELD_ERRORS] = ErrorList(['Case currently assigned to a provider'])
        return cleaned_data

    def save(self, user):
        self.case.close()

        super(DeclineAllSpecialistsCaseForm, self).save(user)  # saves the outcome
