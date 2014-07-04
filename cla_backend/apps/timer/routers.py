from rest_framework.routers import DefaultRouter, Route


class TimerRouter(DefaultRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'create'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated routes.
        # Generated using @action or @link decorators on methods of the viewset
        Route(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{methodname}',
            },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]
