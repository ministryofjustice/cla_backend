from rest_framework.viewsets import GenericViewSet


class CompatGenericViewSet(GenericViewSet):
    def post_save(self, obj, created=False):
        pass
