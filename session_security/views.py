from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .middleware import SESSION_KEY


@require_GET
def ping(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return JsonResponse("logout", safe=False)

    now_ts = int(timezone.now().timestamp())
    idle_for = max(int(request.GET.get("idleFor", 0) or 0), 0)
    client_last_activity = now_ts - idle_for
    stored_last_activity = request.session.get(SESSION_KEY, client_last_activity)
    last_activity = max(client_last_activity, stored_last_activity)

    if now_ts - last_activity >= settings.SESSION_SECURITY_EXPIRE_AFTER:
        logout(request)
        return JsonResponse("logout", safe=False)

    request.session[SESSION_KEY] = now_ts
    return JsonResponse(now_ts - last_activity, safe=False)
