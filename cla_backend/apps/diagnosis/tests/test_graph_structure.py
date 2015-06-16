import os
import re
from django.conf import settings
from django.test import TestCase
from lxml import etree


class GraphStructureTestCase(TestCase):
    def _test_graph_structure(self, graph_file):
        graph_path = os.path.join(os.path.dirname(__file__), '../data', graph_file)
        graph = etree.parse(graph_path)
        ns = {'namespaces': {'g': graph.getroot().nsmap[None]}}

        try:
            permanent_id_key = graph.xpath('//g:key[@attr.name="permanent_id"]',
                                           **ns)[0].attrib['id']
            if not permanent_id_key:
                raise ValueError
            permanent_id_xpath = 'g:data[@key="%s"]' % permanent_id_key
        except (KeyError, IndexError, ValueError):
            self.fail('Cannot find graph "permanent_id" key id in %s' % graph_file)

        permanent_id_set = set()
        nodes = graph.xpath('//g:node', **ns)
        for node in nodes:
            node_id = node.attrib['id']
            data_keys = node.xpath(permanent_id_xpath, **ns)
            self.assertEqual(len(data_keys), 1,
                             'Node %s in %s does not have exactly 1 permanent_id key' %
                             (node_id, graph_file))
            permanent_id = data_keys[0].text
            permanent_id_set.add(permanent_id)

        self.assertEqual(len(permanent_id_set), len(nodes),
                         'Not all nodes in %s have a unique permanent id' % graph_file)
        self.assertIn('start', permanent_id_set,
                      'Graph %s must have one node with permanent id "start"' % graph_file)


for _graph_file in [settings.DIAGNOSIS_FILE_NAME, settings.CHECKER_DIAGNOSIS_FILE_NAME]:
    def _outer(_g):
        def _inner(self):
            self._test_graph_structure(_g)

        return _inner

    _test_name = re.sub(r'[^0-9A-Za-z]+', '_', _graph_file)
    setattr(GraphStructureTestCase, 'test_%s' % _test_name.lower(), _outer(_graph_file))
