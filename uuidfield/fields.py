import uuid

from django.db import models


class UUIDField(models.UUIDField):
    """Compatibility shim for legacy django-uuidfield migrations."""

    def __init__(self, *args, **kwargs):
        auto = kwargs.pop("auto", False)
        if auto:
            kwargs.setdefault("default", uuid.uuid4)
            kwargs.setdefault("editable", False)
        super(UUIDField, self).__init__(*args, **kwargs)
