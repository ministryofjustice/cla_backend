# -*- coding: utf-8 -*-
import markdown

from django import forms

from core.admin.fields import MarkdownAdminField, DEFAULT_MARKDOWN_WHITELIST

from ..models import Note


markdown_whitelist = DEFAULT_MARKDOWN_WHITELIST
markdown_whitelist['tags'].extend(['h1', 'h2', 'h3', 'a', 'em', 'table', 'tr',
                                   'th', 'td', 'tbody', 'thead'])
markdown_whitelist['attributes'].extend(['id'])

EXTENSIONS = ['tables']


class NoteModelForm(forms.ModelForm):
    """
    Saves the field body as html version of the raw_body field.
    """
    raw_body = MarkdownAdminField(
        label=u'Body',
        required=False,
        markdown_whitelist=markdown_whitelist,
        extensions=EXTENSIONS)

    class Meta:
        model = Note
        exclude = []

    def save(self, *args, **kwargs):
        self.instance.body = markdown.markdown(
            self.instance.raw_body, extensions=EXTENSIONS)
        return super(NoteModelForm, self).save(*args, **kwargs)

