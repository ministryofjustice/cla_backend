from django import forms


class ProviderAllocationInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # if any form in error => skip
        if any([not form.is_valid() for form in self.forms]):
            return

        categories = []
        for form in self.forms:
            category = form.cleaned_data.get('category')
            if form.cleaned_data.get('DELETE'):
                continue
            if category and category in categories:
                raise forms.ValidationError(
                    'Please specify one and only one allocation per category'
                )
            categories.append(category)

        return self.cleaned_data
