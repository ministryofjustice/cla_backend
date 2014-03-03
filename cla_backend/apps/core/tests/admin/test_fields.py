import unittest

from django import forms

from core.admin.fields import MarkdownAdminField


TEST_MARKDOWN_WHITELIST = {
    'tags': ['strong', 'b', 'i', 'em', 'p'],
    'attributes': [],
    'styles': []
}


class CustomForm(forms.Form):
    text = MarkdownAdminField(required=False, markdown_whitelist=TEST_MARKDOWN_WHITELIST)


class TestMarkdownAdminField(unittest.TestCase):
    def test_tag_not_allowed(self):
        invalid_data = [
            'header\n======',  # header
            ' - List item 1\n - List item 2\n - List item 3',  # list
            '> Blockquote',  # blockquote
            '[description][1]\n\n\n\n[1]: http://www.google.co.uk',  # link
            '    code',  # code
            '<script>javascript</script>'  # raw html
        ]

        for data in invalid_data:
            form = CustomForm(data={
                'text': data
            })
        self.assertFalse(form.is_valid())

    def test_no_errors(self):
        form = CustomForm(
            data={
                'text': '**strong**\n*italic*'
            }
        )
        self.assertTrue(form.is_valid())

    def test_no_required(self):
        form=CustomForm(data={})
        self.assertTrue(form.is_valid())
