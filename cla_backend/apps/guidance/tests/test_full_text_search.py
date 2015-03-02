# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

from guidance.models import Note


class FullTextSearchTestCase(TestCase):
    fixtures = ['initial_guidance_notes']

    def _get_search_results(self, q):
        return Note.objects.word_tree_search(q)

    def assertTitlesEqual(self, search_results, titles):
        self.assertListEqual(titles, [s.title for s in search_results])

    def test_search_results_are_same_as_lunr(self):
        search_results = self._get_search_results('Debt Prompts')
        self.assertEqual(len(search_results), 3)
        titles = [u'Debt Prompts', u'Housing Prompts', u'Zero income prompts']
        self.assertTitlesEqual(search_results, titles)

        search_results = self._get_search_results('prompt')
        self.assertEqual(len(search_results), 13)
        titles = [
            u'Debt Prompts',
            u'Discrimination Prompts',
            u'Domestic violence prompts',
            u'Discrimination in education',
            u'Education prompts',
            u'Family Prompts',
            u'Handling gender reassignment discrimination cases',
            u'Homelessness',
            u'Housing Prompts',
            u'Opening Call',
            u'Special Educational Needs',
            u'Welfare Benefit Prompts',
            u'Zero income prompts'
        ]
        self.assertTitlesEqual(search_results, titles)

        search_results = self._get_search_results('Homelessness')
        self.assertEqual(len(search_results), 3)
        titles = [
            u'Homelessness',
            u'Homelessness',
            u'Housing Prompts'
        ]
        self.assertTitlesEqual(search_results, titles)

    def test_api_endpoint(self):
        url = reverse('call_centre:guidance_note-list')

        response = self.client.get(url, {'search': 'prompt'})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 13)

        response = self.client.get(url, {'search': 'prompt | Debt &'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, {'search': 'qs &^&£^*£@ 3425 $%@£$%£$@& || |||'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, {'search': ''})
        self.assertEqual(response.status_code, 200)