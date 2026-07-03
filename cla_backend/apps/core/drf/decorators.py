def detail_route(methods=["get"], **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for detail requests.
    """

    def decorator(func):
        func.bind_to_methods = methods
        func.detail = True
        func.kwargs = kwargs
        return func

    return decorator


def list_route(methods=["get"], **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for list requests.
    """

    def decorator(func):
        func.bind_to_methods = methods
        func.detail = False
        func.kwargs = kwargs
        return func

    return decorator
