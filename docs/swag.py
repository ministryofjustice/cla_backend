from django.core.exceptions import ImproperlyConfigured
import docutils.nodes as n
import docutils.parsers.rst.directives
import os
import sphinx.util.compat
from sphinx import addnodes

from rest_framework_swagger import docgenerator
from rest_framework_swagger import introspectors
from rest_framework_swagger import urlparser
from django.conf import settings


def import_urls():
    module = None
    attempts = 0
    while not module:
        try:
            module = __import__(settings.ROOT_URLCONF)
        except ImproperlyConfigured as e:
            if attempts > 3:
                raise e
            attempts += 1
    return module





class AutoAPIDoc(sphinx.util.compat.Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def format_response_class(self, response_class_name):
        ret = n.container()
        ret += addnodes.desc_returns(text=response_class_name)
        model = self.models.get(response_class_name)
        props = addnodes.desc_parameterlist()
        for key, property in model['properties'].items():
            pc = n.container()
            if property['required']:
                pc += addnodes.desc_parameter(key, key)
            else:
                pc += addnodes.desc_optional(key, key)


            pc += n.strong(text=' type: %s ' % property['type'])
            allowableValues = property.get('allowableValues')
            if allowableValues:
                allowableValues.pop('valueType', None)
                pc += n.subscript(text=' %s' % allowableValues)

            props += pc
        ret += props
        return ret

    def format_parameters(self, parameters):
        params = addnodes.desc_parameterlist()
        for param in parameters:
            node = n.container()
            if param['required']:
                node += addnodes.desc_parameter(param['name'], param['name'])
            else:
                node += addnodes.desc_optional(param['name'], param['name'])

            node += n.strong(text=' type: %s ' % param['dataType'])
            allowableValues = param.get('allowableValues')
            if allowableValues:
                allowableValues.pop('valueType', None)
                node += n.emphasis(text=' %s' % allowableValues)
            params += node
        return params

    def format_operation(self, operations):
        c = n.container()
        for op in operations:

            p = addnodes.desc(objtype='endpoint')
            p += addnodes.desc_signature('nickname', op['nickname'])
            p += addnodes.desc_addname('method', op['httpMethod'])
            p += addnodes.desc_content(text=op['summary'])
            if 'parameters' in op.keys():
                p += addnodes.desc_annotation(text='Parameters: ')
                params = self.format_parameters(op['parameters'])
                p += params
            if op.get('responseClass'):
                response = self.format_response_class(op['responseClass'])
                p += response
            c += p

        return c

    def format_path(self, path_doc):
        container = n.section(ids=[n.make_id(path_doc['path'])], names=[])
        container += n.title(text=path_doc['path'])
        container.append(n.paragraph(text=path_doc['description']))
        container.append(self.format_operation(path_doc['operations']))
        return container

    def run(self):
        import_urls()
        url_parser = urlparser.UrlParser()
        apis = url_parser.get_apis(filter_path=self.arguments[0])

        dg = docgenerator.DocumentationGenerator()
        doc = dg.generate(apis)
        self.models = dg.get_models(apis)
        return [self.format_path(item) for item in doc]

def setup(Sphinx):
    Sphinx.add_directive('autoapidoc', AutoAPIDoc)

