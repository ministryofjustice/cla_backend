# Thank you to livskiy on stackckoverflow for this one
# http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed

from django.forms.models import model_to_dict


class ModelDiffMixin(object):
    """
    Model mixin that tracks model fields' values and provides some
    useful api that knows what fields have been changed
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    @property
    def get_field_diff(self, field_name):
        """
        returns a diff for field if its changed else None
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves the model and sets initial state
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])
