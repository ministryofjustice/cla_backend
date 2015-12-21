# -*- coding: utf-8 -*-
from reports.models import Export
from rest_framework import serializers


class ExportSerializer(serializers.ModelSerializer):
    link = serializers.CharField(source='link')

    class Meta:
        model = Export
        fields = ('id', 'link', 'path', 'status')
