# coding=utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse

from guidance.models import Note
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin


class FullTextSearchTestCase(CLAOperatorAuthBaseApiTestMixin, TestCase):
    fixtures = ["initial_guidance_notes"]

    def _get_with_auth(self, *args, **kwargs):
        return self.client.get(*args, HTTP_AUTHORIZATION="Bearer %s" % self.token, **kwargs)

    def _get_search_results(self, q):
        return Note.objects.word_tree_search(q)

    def assertTitlesEqual(self, search_results, titles):
        self.assertListEqual(titles, [s.title for s in search_results])

    def test_search_results_are_same_as_lunr(self):
        search_results = self._get_search_results("Debt Prompts")
        self.assertEqual(len(search_results), 3)
        titles = ["Debt Prompts", "Housing Prompts", "Zero income prompts"]
        self.assertTitlesEqual(search_results, titles)

        search_results = self._get_search_results("prompt")
        self.assertEqual(len(search_results), 14)
        titles = [
            "Debt Prompts",
            "Discrimination Prompts",
            "Domestic violence prompts",
            "Discrimination in education",
            "Education prompts",
            "Family Prompts",
            "Handling gender reassignment discrimination cases",
            "Special Educational Needs",
            "Homelessness",
            "Housing Prompts",
            "Opening Call",
            "Welfare Benefit Prompts",
            "Zero income prompts",
            "Disregard prompts",
        ]
        self.assertTitlesEqual(search_results, titles)

        search_results = self._get_search_results("Homelessness")
        self.assertEqual(len(search_results), 3)
        titles = ["Homelessness", "Homelessness", "Housing Prompts"]
        self.assertTitlesEqual(search_results, titles)

    def test_api_endpoint(self):
        url = reverse("call_centre:guidance_note-list")

        response = self._get_with_auth(url, {"search": "prompt"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 14)
        self.assertIn("id", response.data[0])
        self.assertIn("title", response.data[0])

        response = self._get_with_auth(url, {"search": "prompt | Debt &"})
        self.assertEqual(response.status_code, 200)

        response = self._get_with_auth(url, {"search": "qs &^&£^*£@ 3425 $%@£$%£$@& || |||"})
        self.assertEqual(response.status_code, 200)

        response = self._get_with_auth(url, {"search": ""})
        self.assertEqual(response.status_code, 200)

        url = reverse("call_centre:guidance_note-detail", args=["eligibility_check"])

        response = self._get_with_auth(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertIn("body", response.data)
        self.assertIn("title", response.data)
