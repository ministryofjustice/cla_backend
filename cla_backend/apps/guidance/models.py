# -*- coding: utf-8 -*-
from django.db import models

from model_utils.models import TimeStampedModel


class Tag(models.Model):
    title = models.CharField(max_length=100)


class NoteTagRelation(models.Model):
    tag = models.ForeignKey('Tag')
    note = models.ForeignKey('Note')

    class Meta:
        unique_together = (('tag', 'note'),)


class Note(TimeStampedModel):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    body = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='notes', through='NoteTagRelation')
