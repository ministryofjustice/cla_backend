class NestedGenericModelMixin(object):

    nested = False

    def get_parent_lookup_kwarg(self):
        return self.parent_prefix + '_' + self.lookup_field

    def get_parent_queryset(self):
        return self.parent(requet=self.request).get_queryset()

    def get_parent_object(self):
        parent_key = self.kwargs.pop(self.get_parent_lookup_kwarg())
        parent_viewset_instance = self.parent(
            request=self.request,
            kwargs= {self.lookup_field: parent_key})
        parent_obj = parent_viewset_instance.get_object()
        return parent_obj

    def get_object(self):
        is_nested = self.kwargs.get('nested', False)
        if is_nested:
            return getattr(self.get_parent_object(), self.PARENT_FIELD)
        return super(NestedGenericModelMixin, self).get_object()

class AssociateNestedModelToParentMixin(object):


    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'PARENT_FIELD'):
            raise Exception('To use this mixin you must specify PARENT_FIELD')
        super(AssociateNestedModelToParentMixin, self).__init__(*args, **kwargs)

    def post_save(self, obj, created=False):
        """
        associates `obj` to the parent
        :param kwargs: any kwargs needed to work out the parent
        :return: parent_obj after saving it
        """

        if created:
            parent_obj = self.get_parent_object()

            if getattr(parent_obj, self.PARENT_FIELD):
                raise ValueError('%s already has a %s associated to it' % (parent_obj, obj.__class__))
            else:
                setattr(parent_obj, self.PARENT_FIELD, obj)
                parent_obj.save()

        super(AssociateNestedModelToParentMixin, self).post_save(obj, created=created)
