import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ProviderCaseClosureReportForm, OperatorCaseClosureReportForm


@staff_member_required
def provider_closure_volume(request):
    if request.method == 'POST':
        form = ProviderCaseClosureReportForm(request.POST)

        if form.is_valid():
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="provider_closure_volume.csv"'

            writer = csv.writer(response)
            writer.writerow(form.get_headers())
            for row in form.get_rows():
                writer.writerow(row)

            return response
    else:
        form = ProviderCaseClosureReportForm()

    return render(request, 'admin/reports/provider_closure_volume.html', {
            'title': 'Provider Closure Volume',
            'form': form
        })

@staff_member_required
def operator_closure_volume(request):
    if request.method == 'POST':
        form = OperatorCaseClosureReportForm(request.POST)

        if form.is_valid():
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="operator_closure_volume.csv"'

            writer = csv.writer(response)
            writer.writerow(form.get_headers())
            for row in form.get_rows():
                writer.writerow(row)

            return response
    else:
        form = OperatorCaseClosureReportForm()

    return render(
        request,
        'admin/reports/operator_closure_volume.html',
        {
         'title': 'Operator Closure Volume',
         'form': form
        }
    )

