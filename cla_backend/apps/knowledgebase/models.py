from django.db import models
from model_utils.models import TimeStampedModel


class Article(TimeStampedModel):

    organisation = models.CharField(max_length=255, null=True, blank=True)
    service_name = models.CharField(max_length=255, null=True, blank=True)
    service_tag = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    website = models.CharField(max_length=255, null=True, blank=True)
    keywords = models.TextField(blank=True, null=True)
    when_to_use = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    geographic_coverage = models.CharField(
        max_length=255, null=True, blank=True)
    type_of_service = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=10,
                                     choices=(('LEGAL', 'Legal'),
                                              ('OTHER', 'Other')))
    address = models.TextField(blank=True, null=True)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    how_to_use = models.TextField(blank=True, null=True)
    accessibility = models.CharField(max_length=255, null=True, blank=True)

    article_category = models.ManyToManyField('ArticleCategory',
                                              through='ArticleCategoryMatrix')

    def __unicode__(self):
        return self.service_name


class ArticleCategory(TimeStampedModel):
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Article categories"


class ArticleCategoryMatrix(TimeStampedModel):
    article = models.ForeignKey(Article)
    article_category = models.ForeignKey(ArticleCategory)
    preferred_signpost = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s - %s" % (self.article.__unicode__(),
                             self.article_category.__unicode__())

    class Meta:
        verbose_name_plural = "Article category matrices"


class TelephoneNumber(TimeStampedModel):
    article = models.ForeignKey('Article')
    name = models.CharField(max_length=50, blank=True, null=True)
    number = models.CharField(max_length=25)
