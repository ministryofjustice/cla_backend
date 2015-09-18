import contextlib
import csvkit as csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.db import InternalError
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.utils.six import text_type

from .forms import MICaseExtract, MIFeedbackExtract, \
    MIContactsPerCaseByCategoryExtract, MIAlternativeHelpExtract, \
    MISurveyExtract, MICB1Extract, MIVoiceReport, MIEODReport, \
    MIOBIEEExportExtract, MetricsReport, MIDuplicateCaseExtract, \
    ComplaintsReport
from reports.forms import MIDigitalCaseTypesExtract


def csv_download(filename, form):
    response = make_csv_download_response(filename)
    csv_data = list(form)
    with csv_writer(response) as writer:
        map(writer.writerow, csv_data)
    return response


def submit_info(filename, form, template='success_info'):
    tmpl = 'admin/reports/{0}.html'.format(template)
    return render_to_response(tmpl, {'filename': filename, 'form': form})


def report_view(form_class, title, template='case_report', success_action=csv_download, file_name=None):
    def wrapper(fn):
        slug = title.lower().replace(' ', '_')
        if not file_name:
            filename = '{0}.csv'.format(slug)
        else:
            filename = file_name
        tmpl = 'admin/reports/{0}.html'.format(template)

        def view(request):
            form = form_class()

            if valid_submit(request, form):
                try:
                    return success_action(filename, form)
                except InternalError as error:
                    error_message = text_type(error).strip()
                    if 'wrong key' in error_message.lower() or 'corrupt data' in error_message.lower():
                        # e.g. if pgcrypto key is incorrect
                        error_message = 'Check passphrase and try again'
                    else:
                        error_message = u'An error occurred:\n%s' % error_message
                    messages.error(request, error_message)

            return render(request, tmpl, {'title': title, 'form': form})

        return view

    return wrapper


def valid_submit(request, form):
    if request.method == 'POST':
        form.data = request.POST
        form.is_bound = True
        return form.is_valid()
    return False


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
@report_view(MIDuplicateCaseExtract, 'MI Duplicate Case Extract')
def mi_duplicate_case_extract():
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


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIDigitalCaseTypesExtract, 'MI Digital Case Types Report')
def mi_digital_case_type_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIEODReport, 'MI EOD Report')
def mi_eod_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_complaints_report')
@report_view(ComplaintsReport, 'Complaints Report')
def mi_complaints():
    pass


@staff_member_required
@permission_required('legalaid.run_obiee_reports')
@report_view(MIOBIEEExportExtract,
             'MI Export to Email for OBIEE',
             success_action=submit_info,
             file_name='cla.database.zip')
def mi_obiee_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MetricsReport, 'Metrics Report')
def metrics_report():
    pass
