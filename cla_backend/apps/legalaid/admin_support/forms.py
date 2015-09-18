from django import forms
import markdown

from core.admin.fields import MarkdownAdminField
from ..models import Category


class CategoryModelForm(forms.ModelForm):
    """
    Saves the field description as html version of the raw_description field.
    """
    raw_description = MarkdownAdminField(label=u'Description', required=False)

    class Meta(object):
        model = Category
        exclude = []

    def save(self, *args, **kwargs):
        self.instance.description = markdown.markdown(self.instance.raw_description)
        return super(CategoryModelForm, self).save(*args, **kwargs)
