from django import forms
from django.forms import Form
from django.forms.util import ErrorList
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import transaction

from cla_common.constants import MATTER_TYPE_LEVELS

from cla_eventlog import event_registry
from cla_eventlog.forms import EventSpecificLogForm, BaseCaseLogForm

from legalaid.models import Category, MatterType


class RejectCaseForm(EventSpecificLogForm):
    """
    Rejects a case. If the outcome code has 'requires_action_by' == None
    then it sets case.provider_closed field
    """

    LOG_EVENT_KEY = "reject_case"

    def save(self, user):
        code = self.get_event_code()
        event = event_registry.get_event(self.get_event_key())()
        code_data = event.codes[code]

        val = super(RejectCaseForm, self).save(user)

        # if requires_action by == None:
        #   mark case as closed (keep case.provider)
        # else:
        #   reset provider (case not beloging to provider anymore)
        if code_data.get("set_requires_action_by", False) is None:
            self.case.close_by_provider()
        else:  # if requires_action_by == REQUIRES_ACTION_BY.OPERATOR
            self.case.provider = None
            self.case.provider_assigned_at = None
            self.case.save(update_fields=["provider", "provider_assigned_at"])

        return val


class AcceptCaseForm(BaseCaseLogForm):
    """
    Accepts a case and sets case.provider_accepted field
    """

    LOG_EVENT_KEY = "accept_case"

    def save(self, user):
        val = super(AcceptCaseForm, self).save(user)
        self.case.accept_by_provider()
        return val


class CloseCaseForm(BaseCaseLogForm):
    """
    Closes a case and sets case.provider_closed field
    """

    LOG_EVENT_KEY = "close_case"

    is_debt_referral = forms.BooleanField(required=False)

    def clean(self, *args, **kwargs):
        cleaned_data = super(CloseCaseForm, self).clean(*args, **kwargs)

        if self._errors:  # if already in error => skip
            return cleaned_data

        if self.get_is_debt_referral() and not cleaned_data.get("notes"):
            self._errors["notes"] = ErrorList(["This field is required"])
        return cleaned_data

    def get_is_debt_referral(self):
        return self.cleaned_data.get("is_debt_referral")

    def get_kwargs(self):
        kwargs = super(CloseCaseForm, self).get_kwargs()
        kwargs["is_debt_referral"] = self.get_is_debt_referral()
        return kwargs

    def save(self, user):
        val = super(CloseCaseForm, self).save(user)
        self.case.close_by_provider()
        return val


class ReopenCaseForm(BaseCaseLogForm):
    """
    Reopens a case and resets case.provider_closed field
    """

    LOG_EVENT_KEY = "reopen_case"
    NOTES_MANDATORY = True

    def clean(self, *args, **kwargs):
        cleaned_data = super(ReopenCaseForm, self).clean(*args, **kwargs)

        if self._errors:  # if already in error => skip
            return cleaned_data

        if not self.case.provider_closed:
            self._errors[NON_FIELD_ERRORS] = ErrorList(["You can't reopen this case as it's still open"])
        return cleaned_data

    def save(self, user):
        val = super(ReopenCaseForm, self).save(user)
        self.case.reopen_by_provider()
        return val


class SplitCaseForm(BaseCaseLogForm):
    LOG_EVENT_KEY = "split_case"

    category = forms.ModelChoiceField(queryset=Category.objects.all(), to_field_name="code", required=True)
    matter_type1 = forms.ModelChoiceField(
        queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.ONE), to_field_name="code", required=False
    )
    matter_type2 = forms.ModelChoiceField(
        queryset=MatterType.objects.filter(level=MATTER_TYPE_LEVELS.TWO), to_field_name="code", required=False
    )
    internal = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(SplitCaseForm, self).__init__(*args, **kwargs)

    def is_matter_type_valid(self, category, level, choosen_matter_type):
        if choosen_matter_type:
            try:
                MatterType.objects.get(level=level, category=category, code=choosen_matter_type.code)
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

        category = cleaned_data["category"]
        matter_type1 = cleaned_data["matter_type1"]
        matter_type2 = cleaned_data["matter_type2"]
        internal = cleaned_data["internal"]

        # #### GENERAL #####
        non_fields_errors = []

        # validate case.provider == loggedin provider
        if self.case.provider != self.request.user.staff.provider:
            non_fields_errors.append("Only Providers assigned to the Case can split it.")

        # validate that category exists
        if not self.case.eligibility_check or not self.case.eligibility_check.category:
            non_fields_errors.append("The selected Case doesn't have any category associated.")

        # validate that the case has not been previously split already
        if self.case.is_part_of_split():
            non_fields_errors.append("This Case has already been split or it has been generated by another Case")

        if non_fields_errors:
            self._errors[NON_FIELD_ERRORS] = ErrorList(non_fields_errors)
            return cleaned_data

        # #### CATEGORY #####
        if category == self.case.eligibility_check.category:
            self._errors["category"] = ErrorList(["Please choose a different category or law."])
            del cleaned_data["category"]

        # #### MATTER TYPES #####
        if not self.is_matter_type_valid(category, MATTER_TYPE_LEVELS.ONE, matter_type1):
            self._errors["matter_type1"] = ErrorList(
                ["Select a valid choice. That choice is not one of" " the available choices."]
            )
            del cleaned_data["matter_type1"]
        if not self.is_matter_type_valid(category, MATTER_TYPE_LEVELS.TWO, matter_type2):
            self._errors["matter_type2"] = ErrorList(
                ["Select a valid choice. That choice is not one of" " the available choices."]
            )
            del cleaned_data["matter_type2"]

        # #### INTERNAL #####
        can_deal = self.can_provider_deal_with_category(category)
        if internal and not can_deal:
            self._errors["internal"] = ErrorList(
                ["Internal can only be choosen if you can deal with the selected Category of Law."]
            )
            del cleaned_data["internal"]

        return cleaned_data

    @transaction.atomic
    def save(self, user):
        category = self.cleaned_data["category"]
        matter_type1 = self.cleaned_data["matter_type1"]
        matter_type2 = self.cleaned_data["matter_type2"]
        internal = self.cleaned_data["internal"]

        self.new_case = self.case.split(
            user=user,
            category=category,
            matter_type1=matter_type1,
            matter_type2=matter_type2,
            assignment_internal=internal,
        )

        # create 'creat event' for new case
        event = event_registry.get_event("case")()
        event.process(
            self.new_case, status="created", created_by=self.new_case.created_by, notes="Case created by Specialist"
        )

        super(SplitCaseForm, self).save(user)

        return self.new_case

    def save_event(self, user):
        event = event_registry.get_event(self.get_event_key())()
        event.process_split(
            self.new_case, created_by=user, notes=self.get_notes(), context=self.get_context(), **self.get_kwargs()
        )

    def get_kwargs(self):
        kwargs = super(SplitCaseForm, self).get_kwargs()
        kwargs["internal"] = self.cleaned_data["internal"]
        return kwargs


class ProviderExtractForm(Form):
    CHSUserName = forms.CharField(required=True)
    CHSOrganisationID = forms.CharField(required=True)
    CHSPassword = forms.CharField(required=True)
    CHSCRN = forms.CharField(required=True)

    def clean_CHSCRN(self):
        data = self.cleaned_data["CHSCRN"]
        if data:
            data = data.strip().upper()
        return data
