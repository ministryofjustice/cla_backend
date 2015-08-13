# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Category, Complaint


class CategorySerializerBase(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ComplaintSerializerBase(serializers.ModelSerializer):
    category = CategorySerializerBase()

    class Meta:
        model = Complaint
