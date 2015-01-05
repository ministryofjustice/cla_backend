import os
import tempfile
from zipfile import ZipFile
from shutil import rmtree
import contextlib
import csvkit as csv

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

from rest_framework.views import APIView
from rest_framework import permissions

from .forms import MICaseExtract, MIFeedbackExtract, \
    MIContactsPerCaseByCategoryExtract, MIAlternativeHelpExtract, \
    MISurveyExtract, MICB1Extract, MIVoiceReport
from legalaid.utils import diversity
from cla_auth.auth import OBIEESignatureAuthentication


def report_view(form_class, title, template='case_report'):

    def wrapper(fn):
        slug = title.lower().replace(' ', '_')
        csv_filename = '{0}.csv'.format(slug)
        tmpl = 'admin/reports/{0}.html'.format(template)

        def view(request):
            form = form_class()

            if valid_submit(request, form):
                return csv_download(csv_filename, form)

            return render(request, tmpl, {'title': title, 'form': form})

        return view

    return wrapper


def valid_submit(request, form):
    if request.method == 'POST':
        form.data = request.POST
        form.is_bound = True
        return form.is_valid()
    return False


def csv_download(filename, form):
    response = make_csv_download_response(filename)
    csv_data = list(form)
    with csv_writer(response) as writer:
        map(writer.writerow, csv_data)
    return response


@contextlib.contextmanager
def csv_writer(response):
    yield csv.writer(response)


def make_csv_download_response(filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MICaseExtract, 'MI Case Extract')
def mi_case_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIFeedbackExtract, 'MI Feedback Extract')
def mi_feedback_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIContactsPerCaseByCategoryExtract, 'MI Contacts Per Case By Category')
def mi_contacts_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIAlternativeHelpExtract, 'MI Alternative Help Extract')
def mi_alternative_help_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MISurveyExtract, 'MI Survey Extract (ONLY RUN ON DOM1)')
def mi_survey_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MICB1Extract, 'MI CB1 Extract')
def mi_cb1_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIVoiceReport, 'MI Voice Report')
def mi_voice_extract():
    pass


class DBExportView(APIView):
    sql_files = {
        'cases': 'ExportCases.sql',
        'personal_details': 'ExportPersonalDetails.sql',
        'standard': 'ExportStandardTables.sql',
        'media_code_group': 'ExportMediaCodeGroup.sql',
    }

    authentication_classes = (OBIEESignatureAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    filename = 'cla_database.zip'

    def get(self, request, format=None):
        """
        dt_from, dt_to: ISO 8601 datetime string (2014-08-29T23:59:59)
        passphrase: diversity GPG private key passphrase
        """
        dt_from = request.QUERY_PARAMS.get('from', '')
        dt_to = request.QUERY_PARAMS.get('to', '')
        passphrase = request.QUERY_PARAMS.get('passphrase', '')

        export_path = tempfile.mkdtemp()

        for query_name, sql in self.sql_files.items():
            path = os.path.join(os.path.dirname(__file__), 'sql', sql)
            with open(path, 'r') as f:
                query = f.read()

            if query_name == 'personal_details':
                de = "pgp_pub_decrypt(diversity, dearmor('{key}'), %s)::json".\
                    format(
                        key=diversity.get_private_key()
                    )
                query = query.format(diversity_expression=de, path=export_path)
            else:
                query = query.format(path=export_path)

            params = {
                'cases': [dt_from, dt_to],
                'personal_details': [passphrase, dt_from, dt_to],
                'standard': [dt_from, dt_to],
                'media_code_group': [],
            }[query_name]

            cursor = connection.cursor()
            cursor.execute(query, params)

        os.chdir(export_path)
        zip = open(self.filename, 'w+b')

        with ZipFile(zip, 'w') as z:
            for root, dirs, files in os.walk('.'):
                for f in filter(lambda x: x.endswith('.csv'), files):
                    z.write(f)
        zip.seek(0)

        response = HttpResponse(zip.read(),
                                content_type='application/x-zip-compressed')
        response['Content-Disposition'] = ('attachment; filename="%s"' %
                                           self.filename)

        zip.close()
        rmtree(export_path)

        return response
