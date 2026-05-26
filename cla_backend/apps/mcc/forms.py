from cla_backend.apps.cla_provider.forms import SplitBaseCaseForm
from cla_eventlog.forms import BaseCaseLogForm
from django import forms
from legalaid.models import Category
from django.db import transaction
from django.forms.util import ErrorList
from django.core.exceptions import NON_FIELD_ERRORS


class SplitMCCCaseForm(SplitBaseCaseForm):
    # Doesn't care about an `already split` case or if case is being split by `same-category`
    pass


class ChangeCategoryForm(BaseCaseLogForm):
    """
    MCC: Change category
    """

    LOG_EVENT_KEY = "change_category"

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        to_field_name="code",
        required=True
    )
    NOTES_MANDATORY = True

    def get_context(self):
        old_category = self.case.eligibility_check.category if self.case.eligibility_check else None
        new_category = self.cleaned_data["category"]

        return {
            "old_category": old_category.code if old_category else None,
            "new_category": new_category.code if new_category else None,
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ChangeCategoryForm, self).__init__(*args, **kwargs)
        self._old_category = (
            self.case.diagnosis.category
            if getattr(self.case, "diagnosis", None)
            else None)

    def clean(self):
        cleaned_data = super(ChangeCategoryForm, self).clean()

        if self._errors:
            return cleaned_data

        # Ensure provider owns the case (same pattern as split)
        if self.case.provider != self.request.user.staff.provider:
            self._errors[NON_FIELD_ERRORS] = ErrorList([
                "Only Providers assigned to the Case can change its category."
            ])
        return cleaned_data

    @transaction.atomic
    def save(self, user):
        category = self.cleaned_data["category"]
        note = self.cleaned_data["notes"]
        super(ChangeCategoryForm, self).save(user)
        self.case.change_category(category, note, user=user)
        return self.case
