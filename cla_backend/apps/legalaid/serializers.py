from rest_framework import serializers

from .models import Category, EligibilityCheck


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class EligibilityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityCheck
        fields = ('reference', 'category', 'notes')
