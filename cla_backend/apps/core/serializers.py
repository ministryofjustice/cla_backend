from rest_framework import serializers


class UUIDSerializer(serializers.SlugRelatedField):
    def to_native(self, obj):
        return unicode(getattr(obj, self.slug_field))
