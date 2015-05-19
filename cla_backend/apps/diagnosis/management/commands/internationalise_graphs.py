import textwrap
from django.core.management.base import LabelCommand


class Command(LabelCommand):
    """
    This command re-writes graphml files into Django templates internationalising
    certain known attributes
    """
    help = textwrap.dedent(__doc__).strip()
    args = 'path_to_graphml'
    label = 'file_path'

    def handle_label(self, file_path, **options):
        from diagnosis.graph import GraphImporter

        self.stdout.write('Internationalising GraphML file %s' % file_path)
        GraphImporter(file_path).internationalise()
