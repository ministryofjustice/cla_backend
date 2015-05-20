import os
import shlex
import textwrap
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import LabelCommand, CommandError
from django.core.management.utils import popen_wrapper
from django.utils.translation import to_locale
import polib


class Command(LabelCommand):
    """
    Short-cuts for making and compiling Django gettext messages and
    pushing/pulling them with Transifex
    """
    help = textwrap.dedent(__doc__).strip()
    args = 'update|push|pull'
    label = 'action'

    standard_options = {}
    verbosity = 1

    def handle_label(self, label, **options):
        self.standard_options.update(options)  # NB: exclude any custom options specific to this command
        self.verbosity = int(options['verbosity'])

        try:
            getattr(self, 'action_%s' % label)()
        except AttributeError:
            raise CommandError('Unknown action')

    def _run_cmd(self, cmd):
        msgs, errors, status = popen_wrapper(shlex.split(cmd))
        if errors:
            if status != 0:
                raise CommandError('Command `%s` error:\n%s' % (cmd, errors))
            self.stderr.write(errors)
        if msgs:
            self.stdout.write(msgs)
        if status != 0:
            raise CommandError('Command `%s` exited with status %s' % (cmd, status))

    def _messages(self, do_make=True, do_compile=True):
        cwd = os.getcwd()
        os.chdir(settings.PROJECT_ROOT)
        if do_make:
            call_command('makemessages', all=True, keep_pot=True, no_wrap=True, extensions=["html", "txt", "tpl"],
                         **self.standard_options)
        if do_compile:
            call_command('compilemessages', **self.standard_options)
        os.chdir(cwd)

    def action_update(self):
        if self.verbosity:
            self.stdout.write(self.style.MIGRATE_HEADING('Updating Django translation .pot and.po files'))

        def graphml_file_map(graphml_path):
            return os.path.abspath(os.path.join(settings.PROJECT_ROOT, 'apps', 'diagnosis', *graphml_path))

        # internationalise all graphml files
        graphml_paths = [
            ('data', settings.DIAGNOSIS_FILE_NAME),
            ('data', settings.CHECKER_DIAGNOSIS_FILE_NAME),
        ]
        graphml_files = map(graphml_file_map, graphml_paths)
        call_command('internationalise_graphs', *graphml_files, **self.standard_options)

        # make and compile messages
        self._messages()

    def action_push(self):
        if self.verbosity:
            self.stdout.write(self.style.MIGRATE_HEADING('Pushing all translations to Transifex'))

        # push source .pot and all translated .po files to Transifex
        self._run_cmd('tx push --source --translations')

    def action_pull(self):
        if self.verbosity:
            self.stdout.write(self.style.MIGRATE_HEADING('Pulling all translations from Transifex'))
        self.stdout.write(self.style.WARNING('This command will also merge in the latest local strings!'))

        # pull all known translated .po files except the source language from Transifex
        trans_langs = [lang_code for lang_code, lang_name in settings.LANGUAGES if lang_code != settings.LANGUAGE_CODE]
        self._run_cmd('tx pull --force --language=%s' % ','.join(trans_langs))

        # re-normalise/fix Transifex output to match Django's
        source_locale = to_locale(settings.LANGUAGE_CODE)
        translations_path = os.path.join(settings.PROJECT_ROOT, 'translations')
        for lang_code, lang_name in settings.LANGUAGES:
            locale_code = to_locale(lang_code)
            messages_path = os.path.join(translations_path, locale_code, 'LC_MESSAGES', 'django.po')
            messages_path = os.path.abspath(messages_path)
            messages = polib.pofile(messages_path, wrapwidth=0)
            messages.header = messages.metadata['Project-Id-Version']
            messages.metadata['Language'] = messages.metadata['X-Language'] = locale_code
            messages.metadata['X-Source-Language'] = source_locale
            messages.save(messages_path)
        self._messages()
