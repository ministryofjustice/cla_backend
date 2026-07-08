from rest_framework.decorators import action


def detail_route(methods=["get"], **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for detail requests.
    """

    def decorator(func):
        wrapped = action(methods=methods, detail=True, **kwargs)(func)
        wrapped.bind_to_methods = methods
        wrapped.detail = True
        wrapped.kwargs = kwargs
        return wrapped

    return decorator


def list_route(methods=["get"], **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for list requests.
    """

    def decorator(func):
        wrapped = action(methods=methods, detail=False, **kwargs)(func)
        wrapped.bind_to_methods = methods
        wrapped.detail = False
        wrapped.kwargs = kwargs
        return wrapped

    return decorator
