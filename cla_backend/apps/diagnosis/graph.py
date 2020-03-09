import codecs
import hashlib
from os.path import join, abspath, dirname
import re

from django.conf import settings
from django.template.loader import get_template_from_string, Context
from django.utils import translation
from django.utils.encoding import force_text
from django.utils.functional import lazy, SimpleLazyObject
from django.utils.six import text_type
from lxml import etree, objectify
import markdown
import networkx as nx

from cla_common.constants import DIAGNOSIS_SCOPE


class GraphImporter(object):
    KEY_BODY = "body"
    KEY_TITLE = "title"
    KEY_DESCRIPTION = "description"
    KEY_CONTEXT = "context"
    KEY_ORDER = "order"
    KEY_HELP = "help"
    KEY_HEADING = "heading"
    KEY_PERMANENT_ID = "permanent_id"
    KEY_DATA_SAFETY = "data_safety"

    KEY_NODE_GRAPHICS = "nodegraphics"
    KEY_EDGE_GRAPHICS = "edgegraphics"

    def __init__(self, file_path):
        self.file_path = file_path
        self.graph = None
        self.doc = None
        self.ns = None
        self.prop_mapping = None

    def internationalise(self, output_path=None):
        """
        Makes an internationalised Django template of the input graphml
        """
        # NB: objectify does not allow mutation so must use etree
        self.doc = etree.parse(self.file_path)
        self.ns = self.doc.getroot().nsmap[None]
        self.process_properties_declaration(True)

        # drop unnecessary elements from templates
        for key in [self.KEY_NODE_GRAPHICS, self.KEY_EDGE_GRAPHICS]:
            elements = self.xpath_ns(self.doc, '//ns:data[@key="%s"]' % self.prop_mapping[key]["id"])
            for element in elements:
                element.getparent().remove(element)

        internationalised_keys = [self.KEY_BODY, self.KEY_HELP, self.KEY_HEADING]
        internationalised_keys = [self.prop_mapping[key]["id"] for key in internationalised_keys]

        skipped_values = DIAGNOSIS_SCOPE.CHOICES_CONST_DICT.values()

        for data_element in self.xpath_ns(self.doc, "//ns:data"):
            data_type = data_element.attrib.get("key", None)
            text = data_element.text and data_element.text.strip() or ""
            if data_type in internationalised_keys and text:
                if text in skipped_values:
                    continue
                elif u'"' in text or len(text.splitlines()) > 1:
                    data_element.text = u"{%% blocktrans %%}%s{%% endblocktrans %%}" % text
                else:
                    data_element.text = u'{%% trans "%s" %%}' % text

        if not output_path:
            output_path = "%s.tpl" % self.file_path

        with open(output_path, "w+") as output:
            graph_str = etree.tostring(
                self.doc, encoding="UTF-8", xml_declaration=True, standalone=False, pretty_print=True
            )
            output.write(u"{% load i18n %}".encode("utf-8"))
            output.write(graph_str)

    def process(self, is_templated=settings.DIAGNOSES_USE_TEMPLATES):
        with open(self.file_path, "rb") as afile:
            version = hashlib.md5(afile.read()).hexdigest()
        self.graph = nx.MultiDiGraph(version=version)

        with codecs.open(self.file_path, "r", encoding="utf-8") as f:
            # encoding declaration causes problems so deleting it
            g_str = re.sub(r'encoding=("|\')UTF-8("|\')', "", f.read())
            g_str = re.sub(r"{% load .*?%}", "", g_str)

            self.doc = objectify.fromstring(g_str)
            # objectify.deannotate(self.doc, xsi_nil=True, cleanup_namespaces=True)
            self.ns = self.doc.nsmap[None]

            self.process_properties_declaration()
            node_id_map = self.process_nodes(is_templated=is_templated)
            self.process_edges(node_id_map)

        return self.graph

    def xpath_ns(self, el, s):
        return el.xpath(s, namespaces={"ns": self.ns})

    def process_properties_declaration(self, load_additional=False):
        def _get_id_default_dict_for(attr, attr_name="attr.name", element="node"):
            try:
                xpath = '//ns:key[@%s="%s"][@for="%s"]' % (attr_name, attr, element)
                el = self.xpath_ns(self.doc, xpath)[0]
            except IndexError:
                return {"id": None, "default": None}
            d = {"id": el.attrib.get("id")}

            try:
                d["default"] = el.find("ns:default", namespaces={"ns": self.ns}).text
            except AttributeError:
                d["default"] = None

            return d

        self.prop_mapping = {
            self.KEY_BODY: _get_id_default_dict_for("body"),
            self.KEY_TITLE: _get_id_default_dict_for("title"),
            self.KEY_DESCRIPTION: _get_id_default_dict_for("description"),
            self.KEY_CONTEXT: _get_id_default_dict_for("context:xml"),
            self.KEY_ORDER: _get_id_default_dict_for("order"),
            self.KEY_HELP: _get_id_default_dict_for("help"),
            self.KEY_HEADING: _get_id_default_dict_for("heading"),
            self.KEY_PERMANENT_ID: _get_id_default_dict_for("permanent_id"),
            self.KEY_DATA_SAFETY: _get_id_default_dict_for("data_safety"),
        }

        if load_additional:
            self.prop_mapping.update(
                {
                    self.KEY_NODE_GRAPHICS: _get_id_default_dict_for("nodegraphics", "yfiles.type"),
                    self.KEY_EDGE_GRAPHICS: _get_id_default_dict_for("edgegraphics", "yfiles.type", "edge"),
                }
            )

    def process_nodes(self, is_templated=settings.DIAGNOSES_USE_TEMPLATES):  # noqa: C901
        # C901 cc=19 cocumented in LGA-416
        node_id_map = dict()
        context_key = self.prop_mapping[self.KEY_CONTEXT]["id"]

        def _get_text(a_node, translate=True):
            if is_templated and a_node.text and "{%" in a_node.text:
                tpl = get_template_from_string(u"{%% load i18n %%}%s" % a_node.text)
                if translate:
                    return lazy(lambda: tpl.render(Context()), text_type)()
                with translation.override("en"):
                    return tpl.render(Context())
            return a_node.text

        def _get_markdown(_text):
            if is_templated:
                return lazy(lambda: markdown.markdown(force_text(_text)), text_type)()
            return _text

        def _process_context(_node):
            xml_context = self.xpath_ns(_node, 'ns:data[@key="%s"]' % context_key)
            if not xml_context:
                return None
            xml_context = xml_context[0].find("context")

            if xml_context is None:
                return None

            context = {}
            for child in xml_context.getchildren():
                context[child.tag] = _get_text(child)
            return context

        def _get_node_data_value_or_default(_node, key, as_type=None, translate=True):
            attr_key = self.prop_mapping[key]["id"]
            try:
                data_node = self.xpath_ns(_node, 'ns:data[@key="%s"]' % attr_key)[0]
                value = _get_text(data_node, translate=translate)
            except IndexError:
                value = self.prop_mapping[key]["default"]
            if callable(as_type) and value:
                return as_type(value)
            return value

        def str_to_bool(s):
            return s.lower() == "true"

        # looping through the nodes
        nodes = self.xpath_ns(self.doc, "//ns:node")
        for node in nodes:
            node_id = node.attrib["id"]
            permanent_node_id = _get_node_data_value_or_default(node, self.KEY_PERMANENT_ID)
            node_id_map[node_id] = permanent_node_id

            try:
                order = int(_get_node_data_value_or_default(node, self.KEY_ORDER))
            except TypeError:
                order = 9999

            label = _get_node_data_value_or_default(node, self.KEY_BODY)
            if label:
                label = _get_markdown(label)

            help_text = _get_node_data_value_or_default(node, self.KEY_HELP)
            if help_text:
                help_text = _get_markdown(help_text)

            description = _get_node_data_value_or_default(node, self.KEY_DESCRIPTION)
            if description:
                description = _get_markdown(description)

            self.graph.add_node(
                permanent_node_id,
                label=label,
                title=_get_node_data_value_or_default(node, self.KEY_TITLE),
                key=_get_node_data_value_or_default(node, self.KEY_BODY, translate=False),
                order=order,
                context=_process_context(node),
                help_text=help_text,
                heading=_get_node_data_value_or_default(node, self.KEY_HEADING),
                description=description,
                data_safety=_get_node_data_value_or_default(node, self.KEY_DATA_SAFETY, str_to_bool),
            )

        return node_id_map

    def process_edges(self, node_id_map):
        for edge in self.xpath_ns(self.doc, "//ns:edge"):
            source = edge.attrib["source"]
            target = edge.attrib["target"]
            self.graph.add_edge(node_id_map[source], node_id_map[target])


def get_graph(file_name=settings.DIAGNOSIS_FILE_NAME, is_templated=settings.DIAGNOSES_USE_TEMPLATES):
    file_path = join(abspath(dirname(__file__)), "data", file_name)
    if is_templated:
        file_path += ".tpl"
    importer = GraphImporter(file_path)

    return importer.process(is_templated=is_templated)


def get_graph_mock():
    g = nx.DiGraph()
    g.add_node("root", label="what's your problem")
    g.add_node("c1", label="You are my problem")
    g.add_node("c2", label="Don't have any problem")

    g.add_edge("root", "c1")
    g.add_edge("root", "c2")
    return g


graph = SimpleLazyObject(lambda: get_graph())
