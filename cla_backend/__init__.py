from __future__ import absolute_import

# Ensure app is imported for Celery's `shared_task` when Django starts
from .celery import app as celery_app  # noqa: F401
