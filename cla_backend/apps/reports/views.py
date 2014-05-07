import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ProviderCaseClosureReportForm


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
