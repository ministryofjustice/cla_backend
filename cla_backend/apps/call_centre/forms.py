from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
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
            self.base_fields['provider'].choices = [(p.pk, p.name) for p in self.providers]
        super(ProviderAllocationForm, self).__init__(*args, **kwargs)

    def clean_provider(self):
        provider = self.cleaned_data['provider']

        provider_obj = Provider.objects.get(pk=provider)
        self.cleaned_data['provider_obj'] = provider_obj
        return provider

    def clean(self):
        cleaned_data = super(ProviderAllocationForm, self).clean()
        if not self.providers:
            self._errors[NON_FIELD_ERRORS] = ErrorList([
                _(u'There is no provider specified in '
                  u'the system to handle cases of this law category.')
            ])
            del self._errors['provider']
        return cleaned_data

    def get_notes(self):
        notes = self.cleaned_data['notes']
        if not notes and not self.get_is_manual():
            notes = u"Assigned to {provider}".format(provider=self.cleaned_data['provider_obj'].name)
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

    def clean(self):
        cleaned_data = super(DeferAssignmentCaseForm, self).clean()
        if self._errors:  # skip if already in error
            return cleaned_data

        # checking that the case is in a consistent state
        if self.case.provider:
            self._errors[NON_FIELD_ERRORS] = ErrorList(['Case currently assigned to a provider'])
        return cleaned_data


class DeclineAllSpecialistsCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'decline_help'

    def save(self, user):
        self.case.close()

        super(DeclineAllSpecialistsCaseForm, self).save(user)  # saves the outcome


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

class AssociateThirdPartyDetailsCaseForm(forms.Form):

    reference = forms.CharField(required=True, max_length=32)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(AssociateThirdPartyDetailsCaseForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.case.thirdparty_details:
            raise ValidationError(u'There is already a third party associated to this case.')
        return self.cleaned_data

    def save(self, user):
        ref = self.cleaned_data['reference']
        self.case.associate_thirdparty_details(ref)

class AssociateAdaptationDetailsCaseForm(forms.Form):

    reference = forms.CharField(required=True, max_length=32)

    def __init__(self, *args, **kwargs):
        self.case = kwargs.pop('case')
        super(AssociateAdaptationDetailsCaseForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.case.adaptation_details:
            raise ValidationError(u'There is already an adaptation associated to this case.')
        return self.cleaned_data

    def save(self, user):
        ref = self.cleaned_data['reference']
        self.case.associate_adaptation_details(ref)

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
