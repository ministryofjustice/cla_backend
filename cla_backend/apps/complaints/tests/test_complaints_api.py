# -*- coding: utf-8 -*-
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from rest_framework.test import APITestCase


class BaseComplaintTestCase(
    CLAOperatorAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase
):
    API_URL_BASE_NAME = 'complaints'
    RESOURCE_RECIPE = 'complaints.complaint'

    @property
    def response_keys(self):
        return [
            'category',
            'full_name',
            'category_of_law',
            'case_reference',
            'id',
            'created',
            'modified',
            'eod',
            'description',
            'source',
            'level',
            'justified',
            'owner',
            'created_by'
        ]

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

        # ### DETAIL
        self._test_delete_not_allowed(self.detail_url)

    def test_response_keys(self):
        self.maxDiff = None
        self.assertResponseKeys(response=self.client.get(self.detail_url))
