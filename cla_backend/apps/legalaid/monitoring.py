from django.utils.text import slugify
from django_statsd.clients import statsd


def get_case_category_slug(case):
    if case.diagnosis and case.diagnosis.category:
        return slugify(case.diagnosis.category.code)

def get_provider_slug(provider):
    return slugify(provider) if isinstance(provider, basestring) else slugify(provider.name)

def log_assignment(provider, case):
    provider = get_provider_slug(provider)
    category = get_case_category_slug(case)
    keys = ['ALL']
    if category:
        keys.append(category)

    for c in keys:
        statsd.incr('allocation.{provider}.{category}.assign'.format(provider=provider, category=c))

def log_preallocate(provider, case, add=True):
    provider = get_provider_slug(provider)
    category = get_case_category_slug(case)
    keys = ['ALL']
    if category:
        keys.append(category)

    for c in keys:
        if add:
            statsd.incr('allocation.{provider}.{category}.preallocate'.format(provider=provider, category=c))
        else:
            statsd.decr('allocation.{provider}.{category}.preallocate'.format(provider=provider, category=c))
