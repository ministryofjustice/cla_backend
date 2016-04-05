import json
import re
import boto

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.conf import settings

from .forms import MICaseExtract, MIFeedbackExtract, \
    MIContactsPerCaseByCategoryExtract, MIAlternativeHelpExtract, \
    MISurveyExtract, MICB1Extract, MIVoiceReport, MIEODReport, \
    MIOBIEEExportExtract, MetricsReport, MIDuplicateCaseExtract, \
    ComplaintsReport, MIDigitalCaseTypesExtract, MIProviderAllocationExtract
from reports.models import Export
from .tasks import ExportTask, OBIEEExportTask


def report_view(form_class, title, template='case_report',
                success_task=ExportTask, file_name=None):
    def wrapper(fn):
        slug = re.sub('[^0-9a-zA-Z]+', '_', title.lower()).strip('_')
        if not file_name:
            filename = '{0}.csv'.format(slug)
        else:
            filename = file_name
        tmpl = 'admin/reports/{0}.html'.format(template)

        def view(request):
            form = form_class()

            if valid_submit(request, form):
                success_task().delay(request.user.pk, filename,
                                     form_class.__name__,
                                     json.dumps(request.POST))

                messages.info(request, u'Your export is being processed. It '
                                        u'will show up in the downloads tab '
                                        u'shortly.')

            return render(request, tmpl, {'title': title, 'form': form})

        return view

    return wrapper


def valid_submit(request, form):
    if request.method == 'POST':
        form.data = request.POST
        form.is_bound = True
        return form.is_valid()
    return False


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MIProviderAllocationExtract, 'MI Provider Allocation')
def mi_provider_allocation_extract():
    pass


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
             file_name='cla.database.zip',
             success_task=OBIEEExportTask)
def mi_obiee_extract():
    pass


@staff_member_required
@permission_required('legalaid.run_reports')
@report_view(MetricsReport, 'Metrics Report')
def metrics_report():
    pass


@staff_member_required
def download_file(request, file_name='', *args, **kwargs):
    conn = boto.connect_s3(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.lookup(settings.AWS_STORAGE_BUCKET_NAME)
    k = bucket.get_key(settings.EXPORT_DIR + file_name)

    if k is None:
        raise Http404("Export does not exist")

    k.open_read()
    headers = dict(k.resp.getheaders())
    response = HttpResponse(k)

    for key, val in headers.items():
        response[key] = val

    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = smart_str('%s%s' % (settings.TEMP_DIR, file_name))

    try:
        export_record = Export.objects.get(
            user_id=request.user.pk,
            path__endswith=file_name
        )
        export_record.delete()
    except Export.DoesNotExist:
        raise Http404("Export does not exist")

    return response
