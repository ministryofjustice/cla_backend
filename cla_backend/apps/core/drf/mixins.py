import jsonpatch
import inspect
import warnings

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import SingleRelatedObjectDescriptor, ReverseSingleRelatedObjectDescriptor
from django.http import Http404

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response as DRFResponse
from rest_framework import status
from rest_framework import mixins


class NoParentReferenceException(BaseException):
    pass


class NestedGenericModelMixin(object):
    def get_parent_lookup_kwarg(self):
        return self.parent_prefix + "_" + self.lookup_field

    # def get_parent_queryset(self):
    #     return self.parent(requet=self.request).get_queryset()

    def get_parent_object(self):
        parent_key = self.kwargs.get(self.get_parent_lookup_kwarg(), None)
        if not parent_key:
            raise NoParentReferenceException("Trying to do a nested lookup on a non-nested viewset")
        parent_viewset_instance = self.parent(request=self.request, kwargs={self.lookup_field: parent_key})
        # LGA-1773 can no longer pass queryset to get_object > drf 3.0, set flag to allow select_related in parent viewset
        parent_viewset_instance.do_select_related = True
        parent_obj = parent_viewset_instance.get_object()
        return parent_obj

    def get_parent_object_or_none(self):
        try:
            return self.get_parent_object()
        except (ObjectDoesNotExist, NoParentReferenceException):
            return None

    def is_one_to_one_nested(self):
        descriptor = getattr(self.parent.queryset.model, self.PARENT_FIELD)
        is_single_related = isinstance(descriptor, SingleRelatedObjectDescriptor)
        is_single_reverse_related = isinstance(descriptor, ReverseSingleRelatedObjectDescriptor)
        return not hasattr(descriptor, "related") or is_single_related or is_single_reverse_related

    def get_object(self):
        if self.is_one_to_one_nested():
            obj = getattr(self.get_parent_object(), self.PARENT_FIELD)
        else:
            obj = super(NestedGenericModelMixin, self).get_object()
        if self.request.method != "POST" and obj is None:
            raise Http404
        return obj

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "PARENT_FIELD"):
            raise Exception("To use this mixin you must specify PARENT_FIELD")
        super(NestedGenericModelMixin, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not self.is_one_to_one_nested():
            qs = getattr(self.get_parent_object(), self.PARENT_FIELD)
            return qs.all()

        return super(NestedGenericModelMixin, self).get_queryset()

    def post_save(self, obj, created=False):
        """
        associates `obj` to the parent
        :param kwargs: any kwargs needed to work out the parent
        :return: parent_obj after saving it
        """
        if not self.is_one_to_one_nested():
            return super(NestedGenericModelMixin, self).post_save(obj, created=created)

        if created:
            parent_obj = self.get_parent_object_or_none()

            if parent_obj:
                if getattr(parent_obj, self.PARENT_FIELD):
                    raise MethodNotAllowed(
                        "POST: %s already has a %s associated to it" % (parent_obj, obj.__class__.__name__)
                    )
                else:
                    setattr(parent_obj, self.PARENT_FIELD, obj)
                    parent_obj.save(update_fields=[self.PARENT_FIELD])

        super(NestedGenericModelMixin, self).post_save(obj, created=created)


class JsonPatchViewSetMixin(object):
    @property
    def jsonpatch(self):
        forwards = jsonpatch.JsonPatch.from_diff(self.__pre_save__, self.__post_save__)
        backwards = jsonpatch.JsonPatch.from_diff(self.__post_save__, self.__pre_save__)
        serializer = self.get_serializer_class()

        return {
            "serializer": ".".join([serializer.__module__, serializer.__name__]),
            "backwards": backwards.patch,
            "forwards": forwards.patch,
        }

    def perform_create(self, serializer):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data

        return super(JsonPatchViewSetMixin, self).perform_create(serializer)

    def perform_update(self, serializer):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data
        super(JsonPatchViewSetMixin, self).perform_update(serializer)

    def post_save(self, obj, created=False, **kwargs):
        super(JsonPatchViewSetMixin, self).post_save(obj, created=created)
        self.__post_save__ = self.get_serializer_class()(obj).data

        return obj


class FormActionMixin(object):
    FORM_ACTION_OBJ_PARAM = "obj"

    def _form_action(self, request, Form, no_body=True, form_kwargs={}):
        obj = self.get_object()

        _form_kwargs = form_kwargs.copy()
        _form_kwargs["data"] = request.DATA
        _form_kwargs[self.FORM_ACTION_OBJ_PARAM] = obj

        form = Form(**_form_kwargs)
        if form.is_valid():
            form.save(request.user)

            if no_body:
                return DRFResponse(status=status.HTTP_204_NO_CONTENT)
            else:
                serializer = self.get_serializer(obj)
                return DRFResponse(serializer.data, status=status.HTTP_200_OK)

        return DRFResponse(dict(form.errors), status=status.HTTP_400_BAD_REQUEST)


class ClaPrePostSaveMixin(object):
    def pre_save(self, obj, created=False):
        caller = inspect.stack()[1][3]
        message = "pre_save has been removed in DRF 3.0"
        if caller == "perform_update" or caller == "perform_create":
            warnings.warn(message, DeprecationWarning)
        else:
            stack = []
            for item in inspect.stack():
                if item[3] == "pre_save":
                    stack.append("{file} {function}:line {line}".format(file=item[1], function=item[3], line=item[2]))
            message = "{message}\nReplace following with perform_create or perform_update:\n {stack}".format(
                message=message, stack="\n".join(stack)
            )
            # raise NotImplementedError(message)
            warnings.warn(message)
            # raise NotImplementedError(message)
            super(ClaPrePostSaveMixin, self).pre_save(obj, created)

    def post_save(self, obj, created=False):
        caller = inspect.stack()[1][3]
        message = "post_save has been removed in DRF 3.0"
        if caller == "perform_update" or caller == "perform_create":
            warnings.warn(message, DeprecationWarning)
        else:
            stack = []
            for item in inspect.stack():
                if item[3] == "post_save":
                    stack.append("{file}:{function}".format(file=item[1], function=item[3]))
            message = "{message}\nReplace following with perform_create or perform_update:\n {stack}".format(
                message=message, stack="\n".join(stack)
            )
            warnings.warn(message)
            # raise NotImplementedError(message)
            super(ClaPrePostSaveMixin, self).post_save(obj, created)


class ClaCreateModelMixin(ClaPrePostSaveMixin, mixins.CreateModelMixin):
    def perform_create(self, serializer):
        self.pre_save(serializer)
        obj = serializer.save()
        self.post_save(serializer.instance, created=True)
        return obj

    def post_save(self, obj, created=False):
        pass


class ClaRetrieveModelMixinWithSelfInstance(mixins.RetrieveModelMixin):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        self.instance = self.get_object()
        serializer = self.get_serializer(self.instance)
        return DRFResponse(serializer.data)


class ClaUpdateModelMixin(ClaPrePostSaveMixin, mixins.UpdateModelMixin):
    def perform_update(self, serializer):
        self.pre_save(serializer.instance)
        super(ClaUpdateModelMixin, self).perform_update(serializer)
        self.post_save(serializer.instance, created=False)

    def post_save(self, obj, created=False):
        pass
