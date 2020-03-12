from django.test import TestCase
from django.conf import settings
from django.core.management import call_command

from cla_common.constants import DIAGNOSIS_SCOPE, MATTER_TYPE_LEVELS
from legalaid.models import Category, MatterType
from diagnosis.graph import get_graph
from diagnosis.utils import get_node_scope_value


class GraphTestCase(TestCase):
    def setUp(self):
        self.graph = get_graph(file_name=settings.DIAGNOSIS_FILE_NAME)
        self.checker_graph = get_graph(file_name=settings.CHECKER_DIAGNOSIS_FILE_NAME)
        call_command("loaddata", "initial_category")
        call_command("loaddata", "initial_mattertype")

    def assertCategoryInContext(self, context, nodes):
        # checking that the category is set and is valid
        category_name = context.get("category")
        try:
            return Category.objects.get(code=category_name)
            # GOOD
        except Category.DoesNotExist:
            self.assertTrue(
                False,
                "None of the nodes in this path (%s) have category set! Or the category doesn't match any record in the database (category: %s)"
                % ("\n".join([node["label"] + " " + node["id"] for node in nodes]), category_name),
            )

    def assertMatterTypesInContext(self, context, category, nodes):
        matter_type1_code = context.get("matter-type-1")
        matter_type2_code = context.get("matter-type-2")
        if matter_type2_code and not matter_type1_code:
            self.assertTrue(
                False,
                "MatterType2 (%s) set but MatterType1 == None for nodes in this path (%s)"
                % (matter_type2_code, "\n".join([node["label"] + " " + node["id"] for node in nodes])),
            )

        self.assertMatterType(matter_type1_code, MATTER_TYPE_LEVELS.ONE, category, nodes)
        self.assertMatterType(matter_type2_code, MATTER_TYPE_LEVELS.TWO, category, nodes)

    def assertMatterType(self, matter_type_code, level, category, nodes):
        if matter_type_code:
            # checking that matter type is valid
            try:
                return MatterType.objects.get(code=matter_type_code, level=level, category=category)
            except MatterType.DoesNotExist:
                self.assertTrue(
                    False,
                    "MatterType (%s) for nodes in this path (%s) doesn't match any record in the database (level %s, category %s)"
                    % (
                        matter_type_code,
                        "\n".join([node["label"] + " " + node["id"] for node in nodes]),
                        level,
                        category.code,
                    ),
                )

    def test_end_nodes_have_category(self):
        def move_down(node_id, context, nodes):
            node = self.graph.node[node_id]
            node["id"] = node_id

            nodes = list(nodes)
            nodes.append(node)

            context = dict(context)
            context.update(node["context"] or {})

            scope_value = get_node_scope_value(self.graph, node_id)
            if scope_value in [DIAGNOSIS_SCOPE.INSCOPE, DIAGNOSIS_SCOPE.OUTOFSCOPE]:
                category = self.assertCategoryInContext(context, nodes)
                self.assertMatterTypesInContext(context, category, nodes)

            for child_id in self.graph.successors(node_id):
                move_down(child_id, context, nodes)

        move_down("start", {}, [])
        move_down("start", {}, [])

    def test_nodes_have_heading(self):
        checker_graph = get_graph(file_name=settings.CHECKER_DIAGNOSIS_FILE_NAME)
        node = checker_graph.node["n43n2"]
        self.assertEqual(node["heading"], u"Choose the option that best describes your debt problem")

    def test_nodes_have_subheading(self):
        _graph = get_graph(file_name=settings.DIAGNOSIS_FILE_NAME)
        node = _graph.node["n97"]
        self.assertEqual(
            node["context"]["subheading"],
            u"If a local authority is involved in taking a child into care and the applicant has received a letter of proceedings or letter of issue sent or client has a court date, a financial assessment is not required",
        )

    def test_nodes_have_description(self):
        _graph = get_graph(file_name=settings.DIAGNOSIS_FILE_NAME)
        node = _graph.node["n404"]
        self.assertEqual(
            unicode(node["description"]),
            u"<p><strong>The client has received a letter of proceedings, letter of issue or have a court date.</strong></p>\n<p>No financial assessment is required.</p>",
        )
