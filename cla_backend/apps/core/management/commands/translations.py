import os
import textwrap
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import LabelCommand, CommandError


class Command(LabelCommand):
    """
    Short-cuts for making and compiling Django gettext messages and
    pushing/pulling them with Transifex
    """
    help = textwrap.dedent(__doc__).strip()
    args = 'update|push|pull'
    label = 'action'

    def handle_label(self, label, **options):
        try:
            getattr(self, 'action_%s' % label)(**options)
        except AttributeError:
            raise CommandError('Unknown action')

    @classmethod
    def action_update(cls, **options):
        def graphml_file_map(graphml_path):
            return os.path.abspath(os.path.join(settings.PROJECT_ROOT, 'apps', 'diagnosis', *graphml_path))
        graphml_paths = [
            ('data', settings.DIAGNOSIS_FILE_NAME),
            ('data', settings.CHECKER_DIAGNOSIS_FILE_NAME),
        ]
        graphml_files = map(graphml_file_map, graphml_paths)
        call_command('internationalise_graphs', *graphml_files, **options)

        cwd = os.getcwd()
        os.chdir(settings.PROJECT_ROOT)
        call_command('makemessages', all=True, keep_pot=True, no_wrap=True, extensions=["html", "txt", "tpl"])
        call_command('compilemessages')
        os.chdir(cwd)

    @classmethod
    def action_push(cls, **options):
        raise NotImplementedError

    @classmethod
    def action_pull(cls, **options):
        raise NotImplementedError
