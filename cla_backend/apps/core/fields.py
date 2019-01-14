from rest_framework.fields import BooleanField


# this will eventually be fixed by DRF, see:
# https://github.com/tomchristie/django-rest-framework/pull/1422
class NullBooleanField(BooleanField):
    # empty = True

    def __init__(self, *args, **kwargs):
        kwargs["required"] = False
        super(NullBooleanField, self).__init__(*args, **kwargs)

    def from_native(self, value):
        if value in ("none", "None", "null", None):
            return None
        return super(NullBooleanField, self).from_native(value)
