# -*- coding: utf-8 -*-
from django.db import models

from model_utils.models import TimeStampedModel


class Tag(models.Model):
    title = models.CharField(max_length=100)

    def __unicode__(self):
        return self.title


class NoteTagRelation(models.Model):
    tag = models.ForeignKey('Tag')
    note = models.ForeignKey('Note')

    class Meta:
        unique_together = (('tag', 'note'),)
        verbose_name = 'Tag'

    def __unicode__(self):
        return u'%s (%s)' % (self.tag.title, self.note.title)


class Note(TimeStampedModel):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    body = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='notes', through='NoteTagRelation')

    def __unicode__(self):
        return self.title
