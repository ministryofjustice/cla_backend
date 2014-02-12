from rest_framework import serializers

from .models import Category, EligibilityCheck, Property


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class EligibilityCheckSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = EligibilityCheck
        fields = ('reference', 'category', 'notes')


class PropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = ('value', 'equity', 'share',)
