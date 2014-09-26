from django.test import TestCase

from django.conf import settings
from django.core.management import call_command

from cla_common.constants import DIAGNOSIS_SCOPE

from legalaid.models import Category

from diagnosis.graph import get_graph
from diagnosis.utils import get_node_scope_value

if not hasattr(settings, 'ORIGINAL_DIAGNOSIS_FILE_NAME'):
    raise Exception(
        'Please set ORIGINAL_DIAGNOSIS_FILE_NAME to the original path_file'
    )


class GraphTestCase(TestCase):

    def setUp(self):
        self.graph = get_graph(
            file_name=settings.ORIGINAL_DIAGNOSIS_FILE_NAME
        )
        call_command('loaddata', 'initial_category')

    def test_end_nodes_have_category(self):
        def move_down(node_id, context, nodes):
            node = self.graph.node[node_id]
            node['id'] = node_id

            nodes = list(nodes)
            nodes.append(node)

            context = dict(context)
            context.update(node['context'] or {})

            scope_value = get_node_scope_value(self.graph, node_id)
            if scope_value in [DIAGNOSIS_SCOPE.INSCOPE, DIAGNOSIS_SCOPE.OUTOFSCOPE]:

                # checking that the category is set
                category_name = context.get('category')
                try:
                    Category.objects.get(code=category_name)
                    # GOOD
                    # print 'checked...'+category_name
                except Category.DoesNotExist:
                    self.assertTrue(False,
                        'None of the nodes in this path (%s) have category set! Or the category doesn\'t match any record in the database (category: %s)' % (
                        '\n'.join([node['label']+' '+node['id'] for node in nodes]), category_name
                    ))

            for child_id in self.graph.successors(node_id):
                move_down(child_id, context, nodes)

        root_id = self.graph.graph['operator_root_id']
        move_down(root_id, {}, [])
