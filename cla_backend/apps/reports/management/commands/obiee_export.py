from django_docopt_command import DocOptCommand

from reports.utils import OBIEEExporter


class Command(DocOptCommand):
    docs = """
    Usage:
        obiee_export <export_path> <diversity_keyphrase> [--datetime-from=<datetime>] [--datetime-to=<datetime>]

    Options:
        -h --help                   Show this screen.
        --datetime-from=<datetime>  ISO 8601 datetime (default midnight yesterday)
        --datetime-to=<datetime>    ISO 8601 datetime (default midnight today)
    """

    filename = 'cla_database.zip'

    def handle_docopt(self, args):
        fp = OBIEEExporter(args['<export_path>'], args['<diversity_keyphrase>'],
                           args['--datetime-from'], args['--datetime-to']).export()

        self.stdout.write(u'Export created at: %s' % fp)
