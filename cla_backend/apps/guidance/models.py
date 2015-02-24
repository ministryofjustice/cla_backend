# -*- coding: utf-8 -*-
from django.db import models

from model_utils.models import TimeStampedModel


class Tag(models.Model):
    title = models.CharField(max_length=50)


class Note(TimeStampedModel):
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    content = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='notes')
