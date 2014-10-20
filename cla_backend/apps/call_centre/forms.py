import datetime

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.util import ErrorList
from django.utils import timezone

from cla_eventlog import event_registry

from legalaid.utils.dates import is_out_of_hours_for_operators

from cla_provider.models import Provider
from cla_eventlog.forms import BaseCaseLogForm, EventSpecificLogForm
from knowledgebase.models import Article


class ProviderAllocationForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'assign_to_provider'

    provider = forms.ChoiceField()
    is_manual = forms.BooleanField(required=False)
    is_spor = forms.BooleanField(required=False)

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
        return u"Assigned to {provider}. {notes}".format(
            provider=self.cleaned_data['provider_obj'].name,
            notes=self.cleaned_data['notes'] or ""
        )

    def get_is_manual(self):
        return self.cleaned_data['is_manual']

    def get_is_spor(self):
        return self.cleaned_data.get('is_spor', False)

    def get_kwargs(self):
        kwargs = super(ProviderAllocationForm, self).get_kwargs()
        kwargs['is_manual'] = self.get_is_manual()
        kwargs['is_spor'] = self.get_is_spor()
        return kwargs

    def get_context(self):
        provider =  self.cleaned_data['provider_obj']
        return {
            'provider': provider.name,
            'provider_id': provider.id
        }
    def save(self, user):
        data = self.cleaned_data

        self.case.assign_to_provider(data['provider_obj'])

        super(ProviderAllocationForm, self).save(user)
        return data['provider_obj']


class DeferAssignmentCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'defer_assignment'


class DeclineHelpCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'decline_help'


class SuspendCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'suspend_case'


class AlternativeHelpForm(EventSpecificLogForm):

    selected_providers = forms.ModelMultipleChoiceField(
        queryset=Article.objects.all(),
        required=False)

    LOG_EVENT_KEY = 'alternative_help'

    def get_notes(self):
        notes = self.cleaned_data.get('notes')
        providers = self.cleaned_data.get('selected_providers', [])

        notes_l = [notes, 'Assigned alternative help:']
        for provider in providers:
            notes_l.append(unicode(provider))

        return '\n'.join(notes_l)

    def get_event_code(self):
        code = self.cleaned_data['event_code']

        category = self.case.eligibility_check.category.code if self.case.eligibility_check and self.case.eligibility_check.category else None

        if code == 'COSPF':
            if category in ('family', 'housing'):
                code = 'SPFN'
            if category in ('debt', 'education', 'discrimination'):
                code = 'SPFM'
        return code

    def save(self, user):
        providers = self.cleaned_data.get('selected_providers', [])

        self.case.assign_alternative_help(user, providers)
        return super(AlternativeHelpForm, self).save(user)


class CallMeBackForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'call_me_back'

    # format "2013-12-29 23:59" always in UTC
    datetime = forms.DateTimeField()

    def _is_dt_too_soon(self, dt):
        return dt <= timezone.now() + datetime.timedelta(minutes=30)

    def _is_dt_out_of_hours(self, dt):
        return is_out_of_hours_for_operators(timezone.localtime(dt))

    def clean_datetime(self):
        dt = self.cleaned_data['datetime']
        dt = dt.replace(tzinfo=timezone.utc)

        if self._is_dt_too_soon(dt):
            raise ValidationError("Specify a date not in the current half hour.")

        if self._is_dt_out_of_hours(dt):
            raise ValidationError("Specify a date within working hours.")
        return dt

    def clean(self):
        """
        Catches further validation errors before the save.
        """
        cleaned_data = super(CallMeBackForm, self).clean()

        if self._errors:  # if already in error => skip
            return cleaned_data

        event = event_registry.get_event(self.get_event_key())()
        try:
            event.get_log_code(case=self.case, **self.get_kwargs())
        except ValueError as e:
            self._errors[NON_FIELD_ERRORS] = ErrorList([
                str(e)
            ])
        return cleaned_data

    def get_notes(self):
        dt = timezone.localtime(self.cleaned_data['datetime'])
        return u"Callback scheduled for {dt}. {notes}".format(
            dt=dt.strftime("%d/%m/%Y %H:%M"),
            notes=self.cleaned_data['notes'] or ""
        )

    def save(self, user):
        super(CallMeBackForm, self).save(user)
        dt = self.cleaned_data['datetime']
        self.case.set_requires_action_at(dt)


class StopCallMeBackForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'stop_call_me_back'

    action = forms.ChoiceField(
        choices=(
            ('cancel', 'Cancel'),
            ('complete', 'complete'),
        )
    )

    def get_kwargs(self):
        action = self.cleaned_data['action']

        kwargs = {}
        kwargs[action] = True
        return kwargs

    def clean(self):
        """
        Catches further validation errors before the save.
        """
        cleaned_data = super(StopCallMeBackForm, self).clean()

        if self._errors:  # if already in error => skip
            return cleaned_data

        event = event_registry.get_event(self.get_event_key())()
        try:
            event.get_log_code(case=self.case, **self.get_kwargs())
        except ValueError as e:
            self._errors[NON_FIELD_ERRORS] = ErrorList([
                str(e)
            ])
        return cleaned_data

    def save(self, user):
        super(StopCallMeBackForm, self).save(user)
        self.case.reset_requires_action_at()
