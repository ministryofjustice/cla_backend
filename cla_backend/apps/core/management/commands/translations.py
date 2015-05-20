import os
import shlex
import textwrap
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import LabelCommand, CommandError
from django.core.management.utils import popen_wrapper


class Command(LabelCommand):
    """
    Short-cuts for making and compiling Django gettext messages and
    pushing/pulling them with Transifex
    """
    help = textwrap.dedent(__doc__).strip()
    args = 'update|push|pull'
    label = 'action'

    verbosity = 1

    def handle_label(self, label, **options):
        self.verbosity = int(options['verbosity'])
        try:
            getattr(self, 'action_%s' % label)(**options)
        except AttributeError:
            raise CommandError('Unknown action')

    def action_update(self, **options):
        if self.verbosity:
            self.stdout.write(self.style.MIGRATE_HEADING('Updating Django translation .pot and.po files'))

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
        call_command('makemessages', all=True, keep_pot=True, no_wrap=True, extensions=["html", "txt", "tpl"], **options)
        call_command('compilemessages', **options)
        os.chdir(cwd)

    def _run(self, cmd):
        msgs, errors, status = popen_wrapper(shlex.split(cmd))
        if errors:
            if status != 0:
                raise CommandError('Command error:\n%s' % errors)
            self.stderr.write(errors)
        if msgs:
            self.stdout.write(msgs)
        if status != 0:
            raise CommandError('Command exited with status %s' % status)

    def action_push(self, **options):
        if self.verbosity:
            self.stdout.write(self.style.MIGRATE_HEADING('Pushing all translations to Transifex'))
        self._run('tx push --source --translations')

    def action_pull(self, **options):
        if self.verbosity:
            self.stdout.write(self.style.MIGRATE_HEADING('Pulling all translations from Transifex'))
        self._run('tx pull --all')
