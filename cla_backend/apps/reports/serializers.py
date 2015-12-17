# -*- coding: utf-8 -*-
from reports.models import Export
from rest_framework import serializers


class ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Export
