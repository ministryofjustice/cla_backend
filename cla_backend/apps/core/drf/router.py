from rest_framework.routers import Route
from rest_framework_nested.routers import \
    NestedSimpleRouter as OriginalNestedSimpleRouter


class NestedSimpleRouter(OriginalNestedSimpleRouter):
    def get_parent_viewset(self):
        parent_viewset_dict = {name: viewset
                               for name, viewset, _
                               in self.parent_router.registry}

        return parent_viewset_dict.get(self.parent_prefix)

    def register(self, prefix, viewset, base_name=None):
        viewset.parent = self.get_parent_viewset()
        viewset.parent_prefix = self.parent_prefix
        return super(NestedSimpleRouter, self).register(prefix, viewset, base_name)


class NestedCLARouter(NestedSimpleRouter):

    routes = [
        # Detail route.
        Route(
            url=r'^{prefix}/$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy',
                'post': 'create'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated routes.
        # Generated using @action or @link decorators on methods of the viewset.
        Route(
            url=r'^{prefix}/{methodname}/$',
            mapping={
                '{httpmethod}': '{methodname}',
                },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]
