#! /Users/marcofucci/workspaces/pythonenv/cla_backend/bin/python
import re
import codecs
import networkx as nx
from lxml import objectify


class GraphImporter(object):
    KEY_BODY = 'body'
    KEY_TITLE = 'title'

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
        def _get_id_value_for(attr):
            el = self.xpath_ns(self.doc, '//ns:key[@attr.name="%s"]' % attr)[0]
            return el.attrib.get('id')

        self.prop_mapping = {
            self.KEY_BODY: _get_id_value_for('body'),
            self.KEY_TITLE: _get_id_value_for('title')
        }

    def process_nodes(self):
        # for item in self.doc.graph.getchildren():
        body_key = self.prop_mapping[self.KEY_BODY]
        title_key = self.prop_mapping[self.KEY_TITLE]

        for node in self.xpath_ns(self.doc, '//ns:node'):
            self.graph.add_node(
                node.attrib['id'],
                label=self.xpath_ns(node, 'ns:data[@key="%s"]' % body_key),
                title=self.xpath_ns(node, 'ns:data[@key="%s"]' % title_key)
            )

    def process_edges(self):
        for edge in self.xpath_ns(self.doc, '//ns:edge'):
            self.graph.add_edge(edge.attrib['source'], edge.attrib['target'])


if __name__ == '__main__':
    importer = GraphImporter('./graph-2014.07.18.graphml')
    graph = importer.process()
