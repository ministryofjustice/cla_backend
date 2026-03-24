import re

from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import title

from reports.urls import urlpatterns

register = template.Library()


@register.assignment_tag
def report_links():
    abbrevs = re.compile(r"(mi|eod|cb1|obiee)", flags=re.IGNORECASE)

    def replace_abbrev(full_name):
        names = full_name.split()
        names = [abbrevs.sub(lambda n: n.group(1).upper(), name) for name in names]
        return u" ".join(names)

    def report_link(x):
        return {
            "name": replace_abbrev(title(x.name.replace(u"_", u" "))),
            "url": reverse("reports:{0}".format(x.name)),
        }

    return map(report_link, urlpatterns)
