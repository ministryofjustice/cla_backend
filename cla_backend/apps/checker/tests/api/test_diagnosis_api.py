# -*- coding: utf-8 -*-
from django.core.management import call_command
from core.tests.test_base import SimpleResourceAPIMixin
from rest_framework.test import APITestCase
from diagnosis.models import DiagnosisTraversal
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin


class DiagnosisAPITestCase(
    CLACheckerAuthBaseApiTestMixin,
    SimpleResourceAPIMixin,
    APITestCase
):
    LOOKUP_KEY = 'reference'
    API_URL_BASE_NAME = 'diagnosis'
    RESOURCE_RECIPE = 'checker.diagnosis'

    def make_resource(self):
        return None

    def setUp(self):
        super(DiagnosisAPITestCase, self).setUp()
        call_command('loaddata', 'initial_category')
        call_command('loaddata', 'initial_mattertype')

    def tearDown(self):
        super(DiagnosisAPITestCase, self).tearDown()
        DiagnosisTraversal.objects.all().delete()

    def test_create(self):
        self.client.post(
            self.list_url, data={}, format='json'
        )

        self.assertEqual(DiagnosisTraversal.objects.count(), 1)

    def test_move(self):
        response = self.client.post(
            self.list_url, data={}, format='json'
        )

        reference = response.data[self.LOOKUP_KEY]

        move_down_url = self.get_detail_url(reference, suffix='move-down')
        move_up_url = self.get_detail_url(reference, suffix='move-up')

        for node_id in ['n43::n2', 'n2']:
            response = self.client.post(
                move_down_url,
                data={'current_node_id': node_id},
                format='json'
            )

        self.assertEqual(response.data.get('category'), 'debt')
        self.assertEqual(len(response.data.get('nodes')), 3)
        self.assertEqual(len(response.data.get('choices')), 0)

        response = self.client.post(
            move_up_url,
            data={},
            format='json'
        )

        self.assertEqual(response.data.get('current_node_id'), 'n43::n2')
        self.assertEqual(response.data.get('category'), None)
        self.assertEqual(len(response.data.get('nodes')), 1)
        self.assertEqual(len(response.data.get('choices')), 4)


