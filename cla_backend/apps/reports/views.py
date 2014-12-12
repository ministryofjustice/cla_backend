import contextlib
import csvkit as csv

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponse

from .forms import MICaseExtract, MIFeedbackExtract, \
    MIContactsPerCaseByCategoryExtract, MIAlternativeHelpExtract, \
    MISurveyExtract, MICB1Extract, MIVoiceReport


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

@report_view(MIVoiceReport, 'MI Voice Report')
def mi_voice_extract():
    pass
