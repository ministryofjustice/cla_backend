from django.test import TestCase

from model_mommy.recipe import Recipe

from legalaid.admin_support.forms import CategoryModelForm
from legalaid.models import Category


category_recipe = Recipe(Category)


class CategoryModelFormTestCase(TestCase):
    def test_save(self):
        category = category_recipe.make()

        data={
            'name': 'Name',
            'order': 0,
            'code': 'code',
            'raw_description': '**strong**'
        }
        form = CategoryModelForm(instance=category, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(category.raw_description, data['raw_description'])
        self.assertEqual(category.description, u'<p><strong>strong</strong></p>')

    def test_save_empty(self):
        category = category_recipe.make(
            raw_description=u'**strong**',
            description=u'<p><strong>strong</strong></p>'
        )

        data={
            'name': 'Name',
            'order': 0,
            'code': 'code',
            'raw_description': ''
        }
        form = CategoryModelForm(instance=category, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(category.raw_description, u'')
        self.assertEqual(category.description, u'')
