import re
import codecs
import networkx as nx
from lxml import objectify

from os.path import join, abspath, dirname

from django.conf import settings
from django.utils.functional import SimpleLazyObject

import markdown


class GraphImporter(object):
    KEY_BODY = 'body'
    KEY_TITLE = 'title'
    KEY_CONTEXT = 'context'
    KEY_OPERATOR_ROOT = 'operator_root'
    KEY_ORDER = 'order'
    KEY_HELP = 'help'

    def __init__(self, file_path):
        self.file_path = file_path
        self.graph = None
        self.doc = None
        self.ns = None
        self.prop_mapping = None

    def process(self):
        self.graph = nx.MultiDiGraph()

        with codecs.open(self.file_path, 'r', encoding="utf-8") as f:
            # encoding declaration causes problems so deleting it
            g_str = re.sub(r'encoding="UTF-8"', '', f.read())

            self.doc = objectify.fromstring(g_str)
            # objectify.deannotate(self.doc, xsi_nil=True, cleanup_namespaces=True)
            self.ns = self.doc.nsmap[None]

            self.process_properties_declaration()
            self.process_nodes()
            self.process_edges()

        return self.graph

    def xpath_ns(self, el, s):
        return el.xpath(s, namespaces={'ns': self.ns})

    def process_properties_declaration(self):
        def _get_id_default_dict_for(attr):
            el = self.xpath_ns(self.doc, '//ns:key[@attr.name="%s"]' % attr)[0]
            d = {'id': el.attrib.get('id')}

            try:
                d['default'] = el['default'].text
            except AttributeError:
                d['default'] = None

            return d

        self.prop_mapping = {
            self.KEY_BODY: _get_id_default_dict_for('body'),
            self.KEY_TITLE: _get_id_default_dict_for('title'),
            self.KEY_CONTEXT: _get_id_default_dict_for('context:xml'),
            self.KEY_OPERATOR_ROOT: _get_id_default_dict_for('operator_root'),
            self.KEY_ORDER: _get_id_default_dict_for('order'),
            self.KEY_HELP: _get_id_default_dict_for('help'),
        }

    def process_nodes(self):
        context_key = self.prop_mapping[self.KEY_CONTEXT]['id']

        def _process_context(node):
            xml_context = self.xpath_ns(node, 'ns:data[@key="%s"]' % context_key)
            if not xml_context:
                return None
            xml_context = xml_context[0].find('context')

            if xml_context is None:
                return None

            context = {}
            for child in xml_context.getchildren():
                context[child.tag] = child.text
            return context

        def _get_node_data_value_or_default(node, key):
            attr_key = self.prop_mapping[key]['id']
            try:
                return self.xpath_ns(node, 'ns:data[@key="%s"]' % attr_key)[0].text
            except IndexError:
                return self.prop_mapping[key]['default']

        # looping through the nodes
        for node in self.xpath_ns(self.doc, '//ns:node'):
            if _get_node_data_value_or_default(
                    node, self.KEY_OPERATOR_ROOT) == 'true':
                self.graph.graph['operator_root_id'] = self.xpath_ns(node, '@id')[0]

            try:
                order = int(_get_node_data_value_or_default(node, self.KEY_ORDER))
            except TypeError:
                order = 9999

            label = _get_node_data_value_or_default(node, self.KEY_BODY)
            if label:
                label = markdown.markdown(label)

            help_text = _get_node_data_value_or_default(node, self.KEY_HELP)
            if help_text:
                help_text = markdown.markdown(help_text)

            self.graph.add_node(
                node.attrib['id'],
                label=label,
                title=_get_node_data_value_or_default(node, self.KEY_TITLE),
                order=order,
                context=_process_context(node),
                help_text=help_text
            )

    def process_edges(self):
        for edge in self.xpath_ns(self.doc, '//ns:edge'):
            self.graph.add_edge(edge.attrib['source'], edge.attrib['target'])


def get_graph():
    file_path = join(abspath(dirname(__file__)), 'data', settings.DIAGNOSIS_FILE_NAME)
    importer = GraphImporter(file_path)

    return importer.process()


def get_graph_mock():
    G = nx.DiGraph()
    G.add_node('root', label="what's your problem")
    G.add_node('c1', label="You are my problem")
    G.add_node('c2', label="Don't have any problem")

    G.add_edge('root', 'c1')
    G.add_edge('root', 'c2')
    return G


graph = SimpleLazyObject(lambda: get_graph())
