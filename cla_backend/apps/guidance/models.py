# coding=utf-8
import re

from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models

from model_utils.models import TimeStampedModel


class NoteQuerySet(models.QuerySet):
    def word_tree_search(self, query):
        tokens = re.findall(r"[\w'-]+", query or "")
        if not tokens:
            return self

        # Keep a permissive search parser while still supporting prefix matching.
        raw_query = " & ".join("{}:*".format(token) for token in tokens)
        search_query = SearchQuery(raw_query, search_type="raw")
        return (
            self.annotate(tag_titles=StringAgg("tags__title", delimiter=" ", distinct=True))
            .annotate(
                search=(
                    SearchVector("title", weight="A")
                    + SearchVector("tag_titles", weight="B")
                    + SearchVector("raw_body", weight="D")
                )
            )
            .filter(search=search_query)
            .annotate(rank=SearchRank(models.F("search"), search_query))
            .order_by("-rank", "title")
            .distinct()
        )


class Tag(models.Model):
    title = models.CharField(max_length=100)

    class Meta(object):
        ordering = ("title",)

    def __unicode__(self):
        return self.title


class NoteTagRelation(models.Model):
    tag = models.ForeignKey("Tag", on_delete=models.CASCADE)
    note = models.ForeignKey("Note", on_delete=models.CASCADE)

    class Meta(object):
        unique_together = (("tag", "note"),)
        verbose_name = "Tag"

    def __unicode__(self):
        return "%s (%s)" % (self.tag.title, self.note.title)


class Note(TimeStampedModel):
    title = models.CharField(max_length=100)
    body = models.TextField()
    raw_body = models.TextField()
    name = models.CharField(max_length=50)
    tags = models.ManyToManyField("Tag", related_name="notes", through="NoteTagRelation")

    objects = NoteQuerySet.as_manager()

    def __unicode__(self):
        return self.title
