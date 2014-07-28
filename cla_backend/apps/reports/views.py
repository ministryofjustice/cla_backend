import contextlib
import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ProviderCaseClosure, OperatorCaseClosure, \
    OperatorCaseCreate, OperatorAvgDuration, Reallocation, DuplicateMatters


def report_view(form_class, title):

    def wrapper(fn):
        slug = title.lower().replace(' ', '_')
        csv_filename = '{0}.csv'.format(slug)
        template = 'admin/reports/{0}.html'.format(slug)

        def view(request):
            form = form_class()

            if valid_submit(request, form):
                return csv_download(csv_filename, form)

            return render(request, template, {'title': title, 'form': form})

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
    with csv_writer(response) as writer:
        write_form_csv(writer, form)
        return response


@contextlib.contextmanager
def csv_writer(response):
    yield csv.writer(response)


def make_csv_download_response(filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="{0}"'.format(filename)
    return response


def write_form_csv(writer, form):
    writer.writerow(form.get_headers())
    for row in form.get_rows():
        writer.writerow(row)


@staff_member_required
@report_view(ProviderCaseClosure, 'Provider Closure Volume')
def provider_closure_volume():
    pass


@staff_member_required
@report_view(OperatorCaseClosure, 'Operator Closure Volume')
def operator_closure_volume():
    pass


@staff_member_required
@report_view(OperatorCaseCreate, 'Operator Create Volume')
def operator_create_volume():
    pass


@staff_member_required
@report_view(OperatorAvgDuration, 'Operator Handling Time Average')
def operator_avg_duration():
    pass


@staff_member_required
@report_view(Reallocation, 'Cases Ready for Reallocation to New Provider')
def reallocation():
    pass


@staff_member_required
@report_view(DuplicateMatters, 'Duplicate Matters')
def duplicate_matters():
    pass
