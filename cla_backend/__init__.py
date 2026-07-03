from __future__ import absolute_import

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

# Ensure app is imported for Celery's `shared_task` when Django starts
from .celery import app as celery_app  # noqa: F401
