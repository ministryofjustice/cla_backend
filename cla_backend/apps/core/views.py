from django.views import defaults
from sentry_sdk import capture_message, push_scope


def page_not_found(request, *args, **kwargs):
    with push_scope() as scope:
        scope.set_tag("type", "404")
        scope.set_extra("path", request.path)

        capture_message("Page not found", level="error")

    return defaults.page_not_found(request, *args, **kwargs)
