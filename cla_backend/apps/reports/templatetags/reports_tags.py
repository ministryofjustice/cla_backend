from django import template
from django.core.urlresolvers import reverse

from reports.urls import urlpatterns


register = template.Library()


@register.assignment_tag
def report_links():
    def report_link(x):
        return {
            'name': x.name.replace('_', ' '),
            'url': reverse('reports:{0}'.format(x.name))
        }
    return map(report_link, urlpatterns)
