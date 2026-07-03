from __future__ import absolute_import

import django.core
from django import urls as django_urls
from django.utils import translation

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

# Ensure app is imported for Celery's `shared_task` when Django starts
from .celery import app as celery_app  # noqa: F401
