from rest_framework import serializers

from .models import Category, EligibilityCheck


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class EligibilityCheckSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=500, required=False)

    class Meta:
        model = EligibilityCheck
        fields = ('reference', 'category', 'notes')
