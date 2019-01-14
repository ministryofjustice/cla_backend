from collections import namedtuple, OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch

from rest_framework import views
from rest_framework.routers import BaseRouter, flatten, replace_methodname
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.compat import url
from rest_framework.reverse import reverse
from rest_framework.response import Response

from rest_framework_nested.routers import NestedSimpleRouter as OriginalNestedSimpleRouter


Route = namedtuple("Route", ["url", "mapping", "name", "initkwargs"])
DynamicDetailRoute = namedtuple("DynamicDetailRoute", ["url", "name", "initkwargs"])
DynamicListRoute = namedtuple("DynamicListRoute", ["url", "name", "initkwargs"])


class NestedSimpleRouter(OriginalNestedSimpleRouter):
    def get_parent_viewset(self):
        parent_viewset_dict = {name: viewset for name, viewset, _ in self.parent_router.registry}

        return parent_viewset_dict.get(self.parent_prefix)

    def register(self, prefix, viewset, base_name=None):
        viewset.parent = self.get_parent_viewset()
        viewset.parent_prefix = self.parent_prefix
        return super(NestedSimpleRouter, self).register(prefix, viewset, base_name)


class NestedCLARouter(NestedSimpleRouter):

    routes = [
        # Detail route.
        Route(
            url=r"^{prefix}/$",
            mapping={
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
                "post": "create",
            },
            name="{basename}-detail",
            initkwargs={"suffix": "Instance"},
        ),
        # Dynamically generated routes.
        # Generated using @action or @link decorators on methods of the viewset.
        Route(
            url=r"^{prefix}/{methodname}/$",
            mapping={"{httpmethod}": "{methodname}"},
            name="{basename}-{methodnamehyphen}",
            initkwargs={},
        ),
    ]


class AdvancedSimpleRouter(BaseRouter):
    """
    Borrowed directly from DRF v3.0.2.
    Adds support for list_route and detail_route.
    """

    routes = [
        # List route.
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={"get": "list", "post": "create"},
            name="{basename}-list",
            initkwargs={"suffix": "List"},
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r"^{prefix}/{methodname}{trailing_slash}$", name="{basename}-{methodnamehyphen}", initkwargs={}
        ),
        # Detail route.
        Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"},
            name="{basename}-detail",
            initkwargs={"suffix": "Instance"},
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r"^{prefix}/{lookup}/{methodname}{trailing_slash}$",
            name="{basename}-{methodnamehyphen}",
            initkwargs={},
        ),
    ]

    def __init__(self, trailing_slash=True):
        self.trailing_slash = trailing_slash and "/" or ""
        super(AdvancedSimpleRouter, self).__init__()

    def get_default_base_name(self, viewset):
        """
        If `base_name` is not specified, attempt to automatically determine
        it from the viewset.
        """
        # Note that `.model` attribute on views is deprecated, although we
        # enforce the deprecation on the view `get_serializer_class()` and
        # `get_queryset()` methods, rather than here.
        model_cls = getattr(viewset, "model", None)
        queryset = getattr(viewset, "queryset", None)
        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        assert model_cls, (
            "`base_name` argument not specified, and could "
            "not automatically determine the name from the viewset, as "
            "it does not have a `.queryset` attribute."
        )

        return model_cls._meta.object_name.lower()

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """

        known_actions = flatten([route.mapping.values() for route in self.routes if isinstance(route, Route)])

        # Determine any `@detail_route` or `@list_route` decorated methods on the viewset
        detail_routes = []
        list_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, "bind_to_methods", None)
            detail = getattr(attr, "detail", True)
            if httpmethods:
                if methodname in known_actions:
                    raise ImproperlyConfigured(
                        "Cannot use @detail_route or @list_route "
                        'decorators on method "%s" '
                        "as it is an existing route" % methodname
                    )
                httpmethods = [method.lower() for method in httpmethods]
                if detail:
                    detail_routes.append((httpmethods, methodname))
                else:
                    list_routes.append((httpmethods, methodname))

        ret = []
        for route in self.routes:
            if isinstance(route, DynamicDetailRoute):
                # Dynamic detail routes (@detail_route decorator)
                for httpmethods, methodname in detail_routes:
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(getattr(viewset, methodname).kwargs)
                    ret.append(
                        Route(
                            url=replace_methodname(route.url, methodname),
                            mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                            name=replace_methodname(route.name, methodname),
                            initkwargs=initkwargs,
                        )
                    )
            elif isinstance(route, DynamicListRoute):
                # Dynamic list routes (@list_route decorator)
                for httpmethods, methodname in list_routes:
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(getattr(viewset, methodname).kwargs)
                    ret.append(
                        Route(
                            url=replace_methodname(route.url, methodname),
                            mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                            name=replace_methodname(route.name, methodname),
                            initkwargs=initkwargs,
                        )
                    )
            else:
                # Standard route
                ret.append(route)

        return ret

    def get_method_map(self, viewset, method_map):
        """
        Given a viewset, and a mapping of http methods to actions,
        return a new mapping which only includes any mappings that
        are actually implemented by the viewset.
        """
        bound_methods = {}
        for method, action in method_map.items():
            if hasattr(viewset, action):
                bound_methods[method] = action
        return bound_methods

    def get_lookup_regex(self, viewset, lookup_prefix=""):
        """
        Given a viewset, return the portion of URL regex that is used
        to match against a single instance.

        Note that lookup_prefix is not used directly inside REST rest_framework
        itself, but is required in order to nicely support nested router
        implementations, such as drf-nested-routers.

        https://github.com/alanjds/drf-nested-routers
        """
        base_regex = "(?P<{lookup_prefix}{lookup_field}>{lookup_value})"
        # Use `pk` as default field, unset set.  Default regex should not
        # consume `.json` style suffixes and should break at '/' boundaries.
        lookup_field = getattr(viewset, "lookup_field", "pk")
        lookup_value = getattr(viewset, "lookup_value_regex", "[^/.]+")
        return base_regex.format(lookup_prefix=lookup_prefix, lookup_field=lookup_field, lookup_value=lookup_value)

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(prefix=prefix, lookup=lookup, trailing_slash=self.trailing_slash)
                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                ret.append(url(regex, view, name=name))

        return ret


class AdvancedDefaultRouter(AdvancedSimpleRouter):
    """
    Borrowed directly from DRF v3.0.2.
    The default router extends the AdvancedSimpleRouter, but also adds in a default
    API root view, and adds format suffix patterns to the URLs.
    """

    include_root_view = True
    include_format_suffixes = True
    root_view_name = "api-root"

    def get_api_root_view(self):
        """
        Return a view to use as the API root.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRoot(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, *args, **kwargs):
                ret = OrderedDict()
                for key, url_name in api_root_dict.items():
                    try:
                        ret[key] = reverse(url_name, request=request, format=kwargs.get("format", None))
                    except NoReverseMatch:
                        # Don't bail out if eg. no list routes exist, only detail routes.
                        continue

                return Response(ret)

        return APIRoot.as_view()

    def get_urls(self):
        """
        Generate the list of URL patterns, including a default root view
        for the API, and appending `.json` style format suffixes.
        """
        urls = []

        if self.include_root_view:
            root_url = url(r"^$", self.get_api_root_view(), name=self.root_view_name)
            urls.append(root_url)

        default_urls = super(AdvancedDefaultRouter, self).get_urls()
        urls.extend(default_urls)

        if self.include_format_suffixes:
            urls = format_suffix_patterns(urls)

        return urls
