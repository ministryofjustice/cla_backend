import json
import re

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.conf import settings

from .forms import (
    MICaseExtract,
    MIFeedbackExtract,
    MIContactsPerCaseByCategoryExtract,
    MIAlternativeHelpExtract,
    MISurveyExtract,
    MICB1Extract,
    MICB1ExtractAgilisys,
    MIVoiceReport,
    MIEODReport,
    MIOBIEEExportExtract,
    MetricsReport,
    MIDuplicateCaseExtract,
    ComplaintsReport,
    MIDigitalCaseTypesExtract,
    MIProviderAllocationExtract,
    MIExtractCaseViewAuditLog,
    MIExtractComplaintViewAuditLog,
    AllKnowledgeBaseArticles,
)
from reports.models import Export
from .tasks import ExportTask, OBIEEExportTask
from reports.utils import get_s3_connection


def report_view(request, form_class, title, template="case_report", success_task=ExportTask, file_name=None):
    slug = re.sub("[^0-9a-zA-Z]+", "_", title.lower()).strip("_")
    if not file_name:
        filename = "{0}.csv".format(slug)
    else:
        filename = file_name
    tmpl = "admin/reports/{0}.html".format(template)

    form = form_class()
    if valid_submit(request, form):
        success_task().delay(request.user.pk, filename, form_class.__name__, json.dumps(request.POST))

        messages.info(request, u"Your export is being processed. It will show up in the downloads tab shortly.")

    return render(request, tmpl, {"title": title, "form": form})


def scheduled_report_view(request, form_class, title):
    tmpl = "admin/reports/case_report.html"

    return render(request, tmpl, {"title": title})


def valid_submit(request, form):
    if request.method == "POST":
        form.data = request.POST
        form.is_bound = True
        return form.is_valid()
    return False


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_provider_allocation_extract(request):
    return report_view(request, MIProviderAllocationExtract, "MI Provider Allocation")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_case_extract(request):
    return report_view(request, MICaseExtract, "MI Case Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_feedback_extract(request):
    return report_view(request, MIFeedbackExtract, "MI Feedback Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_duplicate_case_extract(request):
    return report_view(request, MIDuplicateCaseExtract, "MI Duplicate Case Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_contacts_extract(request):
    return report_view(request, MIContactsPerCaseByCategoryExtract, "MI Contacts Per Case By Category")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_alternative_help_extract(request):
    return report_view(request, MIAlternativeHelpExtract, "MI Alternative Help Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_survey_extract(request):
    return report_view(request, MISurveyExtract, "MI Survey Extract (ONLY RUN ON DOM1)")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_cb1_extract(request):
    if settings.SHOW_NEW_CB1:
        return scheduled_report_view(request, MICB1Extract, "MI CB1 Extract")
    else:
        return report_view(request, MICB1Extract, "MI CB1 Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_cb1_extract_agilisys(request):
    return report_view(request, MICB1ExtractAgilisys, "MI CB1 Extract for Agilisys")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_voice_extract(request):
    return report_view(request, MIVoiceReport, "MI Voice Report")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_digital_case_type_extract(request):
    return report_view(request, MIDigitalCaseTypesExtract, "MI Digital Case Types Report")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_eod_extract(request):
    return report_view(request, MIEODReport, "MI EOD Report")


@staff_member_required
@permission_required("legalaid.run_complaints_report")
def mi_complaints(request):
    return report_view(request, ComplaintsReport, "Complaints Report")


@staff_member_required
@permission_required("legalaid.run_obiee_reports")
def mi_obiee_extract(request):
    return report_view(
        request,
        MIOBIEEExportExtract,
        "MI Export to Email for OBIEE",
        file_name="cla.database.zip",
        success_task=OBIEEExportTask,
    )


@staff_member_required
@permission_required("legalaid.run_reports")
def metrics_report(request):
    return report_view(request, MetricsReport, "Metrics Report")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_case_view_audit_log_extract(request):
    report_view(request, MIExtractCaseViewAuditLog, "MI Case Views Audit Log Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def mi_complaint_view_audit_log_extract(request):
    report_view(request, MIExtractComplaintViewAuditLog, "MI Complaints Views Audit Log Extract")


@staff_member_required
@permission_required("legalaid.run_reports")
def all_knowledgebase_articles(request):
    report_view(request, AllKnowledgeBaseArticles, "Knowledge Base Articles")


@staff_member_required
def download_file(request, file_name="", *args, **kwargs):
    conn = get_s3_connection()
    bucket = conn.lookup(settings.AWS_REPORTS_STORAGE_BUCKET_NAME)
    k = bucket.get_key(settings.EXPORT_DIR + file_name)

    if k is None:
        raise Http404("Export does not exist")

    k.open_read()
    headers = dict(k.resp.getheaders())
    response = HttpResponse(k)

    for key, val in headers.items():
        response[key] = val

    response["Content-Disposition"] = "attachment; filename=%s" % smart_str(file_name)
    response["X-Sendfile"] = smart_str("%s%s" % (settings.TEMP_DIR, file_name))

    if "scheduled" not in file_name:
        delete_record(request.user.pk, file_name)

    return response


def delete_record(user_id, file_name):
    try:
        export_record = Export.objects.get(user_id=user_id, path__endswith=file_name)
        export_record.delete()
    except Export.DoesNotExist:
        raise Http404("Export does not exist")
