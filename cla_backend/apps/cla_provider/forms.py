from django import forms
from django.forms.util import ErrorList
from django.core.exceptions import NON_FIELD_ERRORS

from cla_eventlog.forms import EventSpecificLogForm, BaseCaseLogForm
from cla_common.constants import MATTER_TYPE_LEVELS

from legalaid.models import Category, MatterType


class RejectCaseForm(EventSpecificLogForm):
    LOG_EVENT_KEY = 'reject_case'


class AcceptCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'accept_case'


class CloseCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'close_case'


class SplitCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = 'split_case'

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        to_field_name='code', required=True
    )
    matter_type1 = forms.ModelChoiceField(
        queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.ONE),
        to_field_name='code', required=True
    )
    matter_type2 = forms.ModelChoiceField(
        queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.TWO),
        to_field_name='code', required=True
    )
    internal = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SplitCaseForm, self).__init__(*args, **kwargs)

    def is_matter_type_valid(self, category, level, choosen_matter_type):
        try:
            MatterType.objects.get(
                level=level, category=category,
                code=choosen_matter_type.code
            )
        except MatterType.DoesNotExist:
            return False

        return True

    def can_provider_deal_with_category(self, category):
        provider = self.request.user.staff.provider
        return provider.law_category.filter(code=category.code).count() == 1

    def clean(self):
        cleaned_data = super(SplitCaseForm, self).clean()

        if self._errors:
            return cleaned_data

        category = cleaned_data['category']
        matter_type1 = cleaned_data['matter_type1']
        matter_type2 = cleaned_data['matter_type2']
        internal = cleaned_data['internal']

        ##### GENERAL #####
        non_fields_errors = []

        # validate case.provider == loggedin provider
        if self.case.provider != self.request.user.staff.provider:
            non_fields_errors.append(
                'Only Providers assigned to the Case can split it.'
            )

        # validate that category exists
        if not self.case.eligibility_check or not self.case.eligibility_check.category:
            non_fields_errors.append(
                'The selected Case doesn\'t have any category associated.'
            )
        if non_fields_errors:
            self._errors[NON_FIELD_ERRORS] = ErrorList(non_fields_errors)
            return cleaned_data

        ##### CATEGORY #####
        if category == self.case.eligibility_check.category:
            self._errors['category'] = ErrorList([
                'Select a valid choice. That choice is not one of'
                ' the available choices.'
            ])
            del cleaned_data['category']

        ##### MATTER TYPES #####
        if not self.is_matter_type_valid(category, MATTER_TYPE_LEVELS.ONE, matter_type1):
            self._errors['matter_type1'] = ErrorList([
                'Select a valid choice. That choice is not one of'
                ' the available choices.'
            ])
            del cleaned_data['matter_type1']
        if not self.is_matter_type_valid(category, MATTER_TYPE_LEVELS.TWO, matter_type2):
            self._errors['matter_type2'] = ErrorList([
                'Select a valid choice. That choice is not one of'
                ' the available choices.'
            ])
            del cleaned_data['matter_type2']

        ##### INTERNAL #####
        can_deal = self.can_provider_deal_with_category(category)
        if internal and not can_deal:
            self._errors['internal'] = ErrorList([
                'Internal can only be choosen if you can deal with the selected Category of Law.'
            ])
            del cleaned_data['internal']

        return cleaned_data

    def save(self, user):
        category = self.cleaned_data['category']
        matter_type1 = self.cleaned_data['matter_type1']
        matter_type2 = self.cleaned_data['matter_type2']
        internal = self.cleaned_data['internal']

        new_case = self.case.split(
            user=user, category=category,
            matter_type1=matter_type1, matter_type2=matter_type2,
            assignment_internal=internal
        )

        return super(SplitCaseForm, self).save(user)

    def get_kwargs(self):
        kwargs = super(SplitCaseForm, self).get_kwargs()
        kwargs['internal'] = self.cleaned_data['internal']
        return kwargs
