from .models import Timer


def get_timer(request):
    try:
        return Timer.running_objects.get_by_user(request.user.pk)
    except IndexError:
        pass
    return None


def create_timer(request):
    current_timer = get_timer(request)

    if current_timer:
        raise ValueError(u'There is already a timer running. Stop that first.')

    if not request.user.is_authenticated():
        raise ValueError(u'A timer cannot be started without an authenticated User')

    timer = Timer.start(request.user)
    return timer


def stop_timer(request):
    current_timer = get_timer(request)

    if not current_timer:
        raise ValueError(u'No timer found')

    current_timer.stop()
