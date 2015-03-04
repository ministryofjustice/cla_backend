import markdown
import bleach

from django import forms
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

from pagedown.widgets import AdminPagedownWidget


DEFAULT_MARKDOWN_WHITELIST = {
    'tags': ['strong', 'b', 'ul', 'li', 'ol', 'p'],
    'attributes': [],
    'styles': []
}


class MarkdownAdminField(forms.CharField):
    """
    Markdown Admin Field which uses AdminPagedownWidget as default widget and
    supports whitelist validation.

    The extra parameter 'markdown_whitelist' manages the specific tags,
    attributes and styles allowed.
    The value is a dict of this form:
        {
            'tags': ['strong', 'b', 'ul', 'li', 'ol', 'p'],
            'attributes': {
                'a': ['href', 'title'],
                'abbr': ['title'],
                'acronym': ['title'],
            },
            'styles': ['color', 'font-weight']
        }

    The default value is defined by DEFAULT_MARKDOWN_WHITELIST
    """
    def __init__(self, *args, **kwargs):
        self.extensions = kwargs.pop('extensions', [])

        if 'widget' not in kwargs:
            kwargs['widget'] = AdminPagedownWidget(extensions=self.extensions)

        self.markdown_whitelist = kwargs.pop(
            'markdown_whitelist', DEFAULT_MARKDOWN_WHITELIST
        )

        super(MarkdownAdminField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        value = super(MarkdownAdminField, self).clean(*args, **kwargs)

        html_value = markdown.markdown(value, extensions=['markdown.extensions.%s' % e for e in self.extensions])
        bleached_html = bleach.clean(html_value, **self.markdown_whitelist)

        if html_value != bleached_html:
            raise exceptions.ValidationError(
                u'%s%s' % (
                    _(u'One or more tags not allowed. Allowed tags: '),
                    ', '.join(self.markdown_whitelist['tags'])
                )
            )
        return value
