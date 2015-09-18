# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Note


class NoteSearchSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Note
        fields = ('id', 'name', 'title')


class NoteSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Note
        fields = ('body', 'name', 'title')
