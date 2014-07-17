from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Model
from rest_framework.exceptions import MethodNotAllowed


class NoParentReferenceException(BaseException):
    pass


class NestedGenericModelMixin(object):

    def get_parent_lookup_kwarg(self):
        return self.parent_prefix + '_' + self.lookup_field

    def get_parent_queryset(self):
        return self.parent(requet=self.request).get_queryset()

    def get_parent_object(self):
        parent_key = self.kwargs.get(self.get_parent_lookup_kwarg(), None)
        if not parent_key:
            raise NoParentReferenceException('Trying to do a nested lookup on a non-nested viewset')
        parent_viewset_instance = self.parent(
            request=self.request,
            kwargs= {self.lookup_field: parent_key})
        parent_obj = parent_viewset_instance.get_object()
        return parent_obj

    def get_parent_object_or_none(self):
        try:
            return self.get_parent_object()
        except (ObjectDoesNotExist, NoParentReferenceException):
            return None

    def get_object(self):
        return getattr(self.get_parent_object(), self.PARENT_FIELD)


    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'PARENT_FIELD'):
            raise Exception('To use this mixin you must specify PARENT_FIELD')
        super(NestedGenericModelMixin, self).__init__(*args, **kwargs)

    def post_save(self, obj, created=False):
        """
        associates `obj` to the parent
        :param kwargs: any kwargs needed to work out the parent
        :return: parent_obj after saving it
        """

        if created:
            parent_obj = self.get_parent_object_or_none()

            if parent_obj:
                if getattr(parent_obj, self.PARENT_FIELD):
                    raise MethodNotAllowed('POST: %s already has a %s associated to it' % (parent_obj, obj.__class__.__name__))
                else:
                    setattr(parent_obj, self.PARENT_FIELD, obj)
                    parent_obj.save()

        super(NestedGenericModelMixin, self).post_save(obj, created=created)
