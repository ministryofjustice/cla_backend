from __future__ import absolute_import

import inspect
import django.core
from django.db import models as django_models
from django.conf import urls as django_conf_urls
from django import urls as django_urls
from django import utils as django_utils
from django.utils import encoding as django_encoding
from django.utils import translation
import six

if not hasattr(inspect, "getargspec"):
    from collections import namedtuple

    ArgSpec = namedtuple("ArgSpec", ["args", "varargs", "keywords", "defaults"])

    def _getargspec(func):
        spec = inspect.getfullargspec(func)
        return ArgSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)

    inspect.getargspec = _getargspec

# Legacy dependencies still import removed Django translation aliases.
if not hasattr(translation, "ugettext"):
    translation.ugettext = translation.gettext
if not hasattr(translation, "ugettext_lazy"):
    translation.ugettext_lazy = translation.gettext_lazy
if not hasattr(translation, "ungettext"):
    translation.ungettext = translation.ngettext
if not hasattr(translation, "ungettext_lazy"):
    translation.ungettext_lazy = translation.ngettext_lazy

# Legacy dependencies still import the removed django.core.urlresolvers module.
if not hasattr(django.core, "urlresolvers"):
    django.core.urlresolvers = django_urls

# Legacy dependencies still import django.conf.urls.url.
if not hasattr(django_conf_urls, "url"):
    django_conf_urls.url = django_urls.re_path

# Legacy modules still import django.utils.six.
if not hasattr(django_utils, "six"):
    django_utils.six = six

# Legacy dependencies still import removed text encoding aliases.
if not hasattr(django_encoding, "force_text"):
    django_encoding.force_text = django_encoding.force_str
if not hasattr(django_encoding, "smart_text"):
    django_encoding.smart_text = django_encoding.smart_str


# Legacy models and migrations still use removed NullBooleanField.
class _LegacyNullBooleanField(django_models.BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("default", None)
        super(_LegacyNullBooleanField, self).__init__(*args, **kwargs)


django_models.NullBooleanField = _LegacyNullBooleanField

# Ensure app is imported for Celery's `shared_task` when Django starts
from .celery import app as celery_app  # noqa: F401,E402
