from rest_framework.routers import DefaultRouter, Route


class SingletonRouter(DefaultRouter):
    """
    Use this router instead of the DRF DefaultRouter if you have
    only one resource accessible from an endpoint.

    This gives you the following urls:

     * prefix/
        GET: returns 404 or the object
        POST: creates the object if it doesn't exist
        PUT: updates the object
        PATCH: updates the object partially
        DELETE: deletes the object

     * prefix/<method>/
        used for @action and @link methods (NOTE: not tested yet)
    """

    routes = [
        # List route.
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={
                "get": "retrieve",
                "post": "create",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            },
            name="{basename}-detail",
            initkwargs={"suffix": "Instance"},
        ),
        # Dynamically generated routes.
        # Generated using @action or @link decorators on methods of the viewset
        Route(
            url=r"^{prefix}/{methodname}{trailing_slash}$",
            mapping={"{httpmethod}": "{methodname}"},
            name="{basename}-{methodnamehyphen}",
            initkwargs={},
        ),
    ]
