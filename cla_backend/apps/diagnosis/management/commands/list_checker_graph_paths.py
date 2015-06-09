from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils.html import strip_tags
from diagnosis.graph import get_graph


class Command(NoArgsCommand):
    """
    Prints a map of possible paths that can be taken through the scope checker graph,
    useful for determining meaning of URL paths in Public e.g. from Google Analytics
    """
    help = 'Prints a map of possible paths that can be taken through the scope checker graph'

    def handle_noargs(self, *args, **options):
        graph = get_graph(settings.CHECKER_DIAGNOSIS_FILE_NAME)
        paths = dict()

        def find_paths(nodes):
            node = nodes[-1]
            children = graph.successors(node)
            for child in children:
                find_paths(nodes + [child])
            if not children:
                path = nodes[1:]
                text = ''
                for node in path:
                    label = graph.node[node]['label']
                    text += ' - %s\n' % strip_tags(label)
                paths['/'.join(path)] = text

        find_paths(['start'])

        print "%d paths in %s\n" % (len(paths), settings.CHECKER_DIAGNOSIS_FILE_NAME)
        for key in sorted(paths):
            print key
            print paths[key]
