import mock

from django.test import TestCase

from rest_framework.exceptions import ParseError

from core.tests.mommy_utils import make_recipe

from cla_common.constants import DIAGNOSIS_SCOPE

from diagnosis.serializers import DiagnosisSerializer
from diagnosis.models import DiagnosisTraversal

from diagnosis.tests.utils import MockedGraph


class DiagnosisSerializerTestCase(TestCase):
    @mock.patch('diagnosis.serializers.graph', new_callable=MockedGraph)
    def __call__(self, runner, mocked_graph, *args, **kwargs):
        self.mocked_graph = mocked_graph

        super(DiagnosisSerializerTestCase, self).__call__(
            runner, *args, **kwargs
        )

    def setUp(self):
        self.category = make_recipe('legalaid.Category', code='debt')

    # GET

    def test_get_with_ongoing_diagnosis(self):
        """
        Tests that the get request from the serializer returns
        expected values when in the middle of a diagnosis
        """
        traversal = DiagnosisTraversal.objects.create(
            current_node_id='2a',
            nodes=[
                self.mocked_graph.get_node_dict('2a')
            ]
        )
        serializer = DiagnosisSerializer(instance=traversal)
        data = serializer.data
        self.assertItemsEqual(data['nodes'], [
            self.mocked_graph.get_node_dict('2a')
        ])
        self.assertItemsEqual(data['choices'], [
            self.mocked_graph.get_node_dict('3aa'),
            self.mocked_graph.get_node_dict('3ab')
        ])
        self.assertEqual(data['current_node_id'], '2a')
        self.assertEqual(data['state'], DIAGNOSIS_SCOPE.UNKNOWN)
        self.assertEqual(data['category'], None)

    def test_get_with_new_diagnosis(self):
        """
        Tests that the get request from the serializer returns
        expected values when new diagnosis
        """
        traversal = DiagnosisTraversal.objects.create()

        serializer = DiagnosisSerializer(instance=traversal)
        data = serializer.data
        self.assertEqual(data['nodes'], None)
        self.assertItemsEqual(data['choices'], [
            self.mocked_graph.get_node_dict('2a'),
            self.mocked_graph.get_node_dict('2b')
        ])
        self.assertEqual(data['current_node_id'], '')
        self.assertEqual(data['state'], DIAGNOSIS_SCOPE.UNKNOWN)
        self.assertEqual(data['category'], None)

    # MOVE DOWN (update)

    def test_move_down_updates_traversal(self):
        """
        Tests that moving down updates the traversal object
        """
        traversal = DiagnosisTraversal.objects.create(
            current_node_id='2a',
            nodes=[
                self.mocked_graph.get_node_dict('2a')
            ]
        )
        serializer = DiagnosisSerializer(
            instance=traversal, data={
                'current_node_id': '3aa'
            }
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()

        traversal = DiagnosisTraversal.objects.get(pk=traversal.pk)
        self.assertEqual(traversal.current_node_id, '3aa')
        self.assertItemsEqual(traversal.nodes, [
            self.mocked_graph.get_node_dict('2a'),
            self.mocked_graph.get_node_dict('3aa')
        ])

    def test_move_down_processes_end_node_directly(self):
        traversal = DiagnosisTraversal.objects.create(
            current_node_id='2a',
            nodes=[
                self.mocked_graph.get_node_dict('2a')
            ]
        )
        serializer = DiagnosisSerializer(
            instance=traversal, data={
                'current_node_id': '3ab'
            }
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()

        traversal = DiagnosisTraversal.objects.get(pk=traversal.pk)
        self.assertEqual(traversal.current_node_id, 'INSCOPE')
        self.assertItemsEqual(traversal.nodes, [
            self.mocked_graph.get_node_dict('2a'),
            self.mocked_graph.get_node_dict('3ab'),
            self.mocked_graph.get_node_dict('INSCOPE')
        ])
        self.assertEqual(traversal.category.code, 'debt')
        self.assertEqual(traversal.state, DIAGNOSIS_SCOPE.INSCOPE)

    # MOVE UP

    def test_move_up_updates_traversal(self):
        traversal = DiagnosisTraversal.objects.create(
            current_node_id='3aa',
            nodes=[
                self.mocked_graph.get_node_dict('2a'),
                self.mocked_graph.get_node_dict('3aa')
            ]
        )
        serializer = DiagnosisSerializer(instance=traversal)

        serializer.move_up()

        traversal = DiagnosisTraversal.objects.get(pk=traversal.pk)
        self.assertEqual(traversal.current_node_id, '2a')
        self.assertItemsEqual(traversal.nodes, [
            self.mocked_graph.get_node_dict('2a')
        ])

    def test_move_up_fails_if_current_node_is_root(self):
        traversal = DiagnosisTraversal.objects.create()
        serializer = DiagnosisSerializer(instance=traversal)

        self.assertRaises(ParseError, serializer.move_up)

    def test_move_up_skips_end_node(self):
        traversal = DiagnosisTraversal.objects.create(
            current_node_id='INSCOPE',
            nodes=[
                self.mocked_graph.get_node_dict('2a'),
                self.mocked_graph.get_node_dict('3ab'),
                self.mocked_graph.get_node_dict('INSCOPE'),
            ],
            category=self.category,
            state=DIAGNOSIS_SCOPE.INSCOPE
        )
        serializer = DiagnosisSerializer(instance=traversal)

        serializer.move_up()

        traversal = DiagnosisTraversal.objects.get(pk=traversal.pk)
        self.assertEqual(traversal.current_node_id, '2a')
        self.assertItemsEqual(traversal.nodes, [
            self.mocked_graph.get_node_dict('2a')
        ])
        self.assertEqual(traversal.category, None)
        self.assertEqual(traversal.state, DIAGNOSIS_SCOPE.UNKNOWN)
