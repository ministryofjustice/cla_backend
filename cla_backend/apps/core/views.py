from django.views import defaults
from sentry_sdk import capture_message


def page_not_found(*args, **kwargs):
    capture_message("Page not found", level="error")

    return defaults.page_not_found(*args, **kwargs)
