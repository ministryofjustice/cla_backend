from .models import Timer


def _create_timer(user):
    return Timer.start(user)


def get_timer(user):
    if not user.is_authenticated():
        raise ValueError(u"User is not authenticated")

    try:
        return Timer.running_objects.get_by_user(user.pk)
    except IndexError:
        pass
    return None


def create_timer(user):
    current_timer = get_timer(user)

    if current_timer:
        raise ValueError(u"There is already a timer running. Stop that first.")

    return _create_timer(user)


def get_or_create_timer(user):
    created = False
    current_timer = get_timer(user)

    if not current_timer:
        current_timer = _create_timer(user)
        created = True
    return current_timer, created


def stop_timer(user):
    current_timer = get_timer(user)

    if not current_timer:
        raise ValueError(u"No timer found")

    current_timer.stop()
