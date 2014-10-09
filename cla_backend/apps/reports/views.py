import contextlib
import csvkit as csv

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ProviderCaseClosure, OperatorCaseClosure, \
    OperatorCaseCreate, CaseReport, NewCasesWithAdaptationCount, \
    CaseVolumeAndAvgDurationByDay, ReferredCasesByCategory, \
    AllocatedCasesNoOutcome, MICaseExtract, MIFeedbackExtract, \
    MIContactsPerCaseByCategoryExtract


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
@report_view(ProviderCaseClosure, 'Provider Closure Volume')
def provider_closure_volume():
    pass


@staff_member_required
@report_view(OperatorCaseClosure, 'Operator Closure Volume')
def operator_closure_volume():
    pass


@staff_member_required
@report_view(CaseReport, 'All Cases')
def all_cases():
    pass


@staff_member_required
@report_view(NewCasesWithAdaptationCount, 'New Cases with Adaptations')
def adaptation_counts():
    pass


@staff_member_required
@report_view(CaseVolumeAndAvgDurationByDay, 'Case Volume and Average Duration by Operator by Day')
def case_volume_avg_duration_by_operator_day():
    pass


@staff_member_required
@report_view(ReferredCasesByCategory, 'Cases Referred to Specialist by Category')
def referred_cases_by_category():
    pass


@staff_member_required
@report_view(AllocatedCasesNoOutcome, 'Allocated Cases with No Outcome')
def allocated_no_outcome():
    pass


@staff_member_required
@report_view(MICaseExtract, 'MI Case Extract')
def mi_case_extract():
    pass

@staff_member_required
@report_view(MIFeedbackExtract, 'MI Feedback Extract')
def mi_feedback_extract():
    pass


@staff_member_required
@report_view(MIContactsPerCaseByCategoryExtract, 'MI Contacts Per Case By Category')
def mi_contacts_extract():
    pass
