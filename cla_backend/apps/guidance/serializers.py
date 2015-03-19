# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Note


class NoteSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'title')


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('body', 'title')
