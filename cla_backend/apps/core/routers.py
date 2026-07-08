from rest_framework.routers import DefaultRouter, DynamicRoute, Route


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
        used for @detail_route and @list_route methods (NOTE: not tested yet)
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
            detail=True,
            initkwargs={"suffix": "Instance"},
        ),
        # Dynamically generated routes.
        # Generated using @detail_route or @list_route decorators on methods of the viewset
        DynamicRoute(
            url=r"^{prefix}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
    ]
