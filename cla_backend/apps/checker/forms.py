from django import forms
from legalaid.forms import BaseCallMeBackForm
from .utils import (
    CallbackTimeSlotCSVImporter,
    callback_capacity_threshold_breached,
    callback_capacity_threshold_breach_send_notification,
)


class WebCallMeBackForm(BaseCallMeBackForm):
    def __init__(self, *args, **kwargs):
        self.requires_action_at = kwargs.pop("requires_action_at")
        super(WebCallMeBackForm, self).__init__(*args, **kwargs)

    def get_requires_action_at(self):
        return self.requires_action_at

    def save(self, user):
        super(WebCallMeBackForm, self).save(user)
        if callback_capacity_threshold_breached(self.case.requires_action_at):
            callback_capacity_threshold_breach_send_notification(self.case.requires_action_at)


class CallbackTimeSlotCSVUploadForm(forms.Form):
    csv_file = forms.FileField(required=True, widget=forms.FileInput(attrs={"accept": ".csv"}))

    csv_file.label = "Callback capacity CSV file"

    def __init__(self, *args, **kwargs):
        super(CallbackTimeSlotCSVUploadForm, self).__init__(*args, **kwargs)
        self.importer = CallbackTimeSlotCSVImporter()
        self.rows = []

    @staticmethod
    def _raise_validation_errors(errors):
        validation_errors = []
        for error in errors:
            validation_errors.append(forms.ValidationError(error))
        raise forms.ValidationError(validation_errors)

    def clean(self):
        cleaned_data = super(CallbackTimeSlotCSVUploadForm, self).clean()
        self.rows, errors = self.importer.parse(cleaned_data["csv_file"])
        if errors:
            self._raise_validation_errors(errors)
        return cleaned_data

    def save(self):
        self.importer.save(self.rows)
