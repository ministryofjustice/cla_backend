from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="add_nonce")
def add_nonce(value, request):
    if hasattr(request, "csp_nonce"):
        value = mark_safe(value.as_widget(attrs={"nonce": request.csp_nonce}))
    return value
