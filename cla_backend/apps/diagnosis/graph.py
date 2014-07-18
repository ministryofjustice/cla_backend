import codecs
import networkx as nx
from lxml import objectify

from os.path import join, abspath, dirname

from django.conf import settings
from django.utils.functional import SimpleLazyObject


class GraphImporter(object):
    def __init__(self, file_path):
        self.graph = nx.MultiDiGraph()

        with codecs.open(file_path, 'r', encoding="utf-8") as f:
            g_str = f.read()
            self.xml_graph = objectify.fromstring(g_str).graph

            for item in self.xml_graph.getchildren():
                self.process_item(item)

    def process_item(self, el):
        node_type = el.tag
        if node_type == 'node':
            self.graph.add_node(el.attrib['id'], label=el.data.text)

        elif node_type == 'edge':
            self.graph.add_edge(el.attrib['source'], el.attrib['target'])


def get_graph():
    file_path = join(abspath(dirname(__file__)), 'data', settings.DIAGNOSIS_FILE_NAME)
    importer = GraphImporter(file_path)

    return importer.graph


def get_graph_mock():
    G = nx.DiGraph()
    G.add_node('root', label="what's your problem")
    G.add_node('c1', label="You are my problem")
    G.add_node('c2', label="Don't have any problem")

    G.add_edge('root', 'c1')
    G.add_edge('root', 'c2')
    return G


graph = SimpleLazyObject(lambda: get_graph())
