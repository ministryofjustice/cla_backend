from django import forms


class KnowledgebaseCsvUploadForm(forms.Form):
    csv_file = forms.FileField(required=True)

    def is_valid(self):
        return True

    def process(self):
        pass
