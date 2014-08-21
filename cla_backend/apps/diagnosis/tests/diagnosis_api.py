import mock

from rest_framework import status

from cla_common.constants import DIAGNOSIS_SCOPE

from cla_eventlog.models import Log

from core.tests.test_base import \
    NestedSimpleResourceAPIMixin

from diagnosis.models import DiagnosisTraversal
from diagnosis.tests.utils import MockedGraph


class DiagnosisAPIMixin(NestedSimpleResourceAPIMixin):
    LOOKUP_KEY = 'case_reference'
    RESOURCE_RECIPE = 'diagnosis.diagnosis'
    API_URL_BASE_NAME = 'diagnosis'
    PARENT_LOOKUP_KEY = 'reference'
    PARENT_RESOURCE_RECIPE = 'legalaid.case'
    PK_FIELD = 'diagnosis'

    @mock.patch('diagnosis.serializers.graph', new_callable=MockedGraph)
    def __call__(self, runner, mocked_graph, *args, **kwargs):
        self.mocked_graph = mocked_graph

        super(DiagnosisAPIMixin, self).__call__(
            runner, *args, **kwargs
        )

    def setUp(self):
        super(DiagnosisAPIMixin, self).setUp()

        self.move_down_url = self.get_detail_url(self.resource_lookup_value, suffix='move-down')
        self.move_up_url = self.get_detail_url(self.resource_lookup_value, suffix='move-up')

    def assertLogEquals(self, log, diagnosis):
        self.assertItemsEqual(log.patch['nodes'], diagnosis.nodes)
        self.assertItemsEqual(log.patch['reference'], unicode(diagnosis.reference))

    def test_delete_doesnt_create_log_with_ongoing_diagnosis(self):
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.count(), 1)

        response = self.client.delete(
            self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertTrue(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(DiagnosisTraversal.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)

    def test_delete_creates_log_with_completed_diagnosis(self):
        self.resource.current_node_id = 'INSCOPE'
        self.resource.nodes = [
            self.mocked_graph.get_node_dict('2a'),
            self.mocked_graph.get_node_dict('3ab'),
            self.mocked_graph.get_node_dict('INSCOPE')
        ]
        self.resource.state = DIAGNOSIS_SCOPE.INSCOPE
        self.resource.save()

        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(DiagnosisTraversal.objects.count(), 1)

        response = self.client.delete(
            self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertTrue(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(DiagnosisTraversal.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 1)

        self.assertLogEquals(Log.objects.all()[0], self.resource)

    def test_move_down_creates_log_when_diagnosis_completes(self):
        # moving down (not completed) => log NOT created
        self.assertEqual(Log.objects.count(), 0)
        response = self.client.post(
            self.move_down_url, data={
                'current_node_id': '2a'
            },
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(Log.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # moving down (completed) => log created
        response = self.client.post(
            self.move_down_url, data={
                'current_node_id': '3ab'
            },
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(Log.objects.count(), 1)
        self.resource = DiagnosisTraversal.objects.get(pk=self.resource.pk)
        self.assertTrue(self.resource.is_state_inscope())

        self.assertLogEquals(Log.objects.all()[0], self.resource)

        # moving up => no extra log record created
        response = self.client.post(
            self.move_up_url, data={},
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(Log.objects.count(), 1)
        self.resource = DiagnosisTraversal.objects.get(pk=self.resource.pk)
        self.assertFalse(self.resource.is_state_inscope())

        # moving down again (completed) => extra log created
        response = self.client.post(
            self.move_down_url, data={
                'current_node_id': '3ab'
            },
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(Log.objects.count(), 2)
        self.resource = DiagnosisTraversal.objects.get(pk=self.resource.pk)
        self.assertTrue(self.resource.is_state_inscope())

        self.assertLogEquals(Log.objects.all()[1], self.resource)
