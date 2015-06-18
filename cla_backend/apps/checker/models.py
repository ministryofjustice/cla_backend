from django.db import models
from model_utils.models import TimeStampedModel
from uuidfield import UUIDField

from cla_common.constants import REASONS_FOR_CONTACTING


class ReasonForContacting(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)
    other_reasons = models.TextField(blank=True)
    referrer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    case = models.ForeignKey('legalaid.Case', blank=True, null=True)

    class Meta(object):
        verbose_name_plural = 'reasons for contacting'
        ordering = ('-created',)

    @classmethod
    def get_category_stats(cls):
        total_count = cls.objects.count()
        # count categories
        data = ReasonForContactingCategory.objects.values_list('category').\
            annotate(count=models.Count('category')).order_by()
        data = dict(data)
        # known categories, preserving order
        categories = [
            {
                'key': choice[0],
                'description': choice[1],
                'percentage': data[choice[0]] if choice[0] in data else 0,
            }
            for choice in REASONS_FOR_CONTACTING.CHOICES
        ]
        # unknown categories (perhaps have been removed)
        for category, count in data.iteritems():
            if category not in REASONS_FOR_CONTACTING.CHOICES_DICT:
                categories.append({
                    'key': category,
                    'description': category,
                    'percentage': count,
                })
        # calculate percentage of all responses that chose each option
        percentage_total = 100.0 / total_count if total_count else 0.0
        for category in categories:
            category['percentage'] *= percentage_total
        return dict(categories=categories, total_count=total_count)

    @property
    def reason_categories(self):
        if self.reasons.count():
            return u', '.join(map(unicode, self.reasons.all()))
        return u'(No categories specified)'

    def __unicode__(self):
        reason_count = self.reasons.count()
        description = u'%d reasons' % reason_count if reason_count else u'No reasons specified'
        if self.case:
            return description + u' (Case: %s)' % self.case.reference
        return description


class ReasonForContactingCategory(models.Model):
    reason_for_contacting = models.ForeignKey(ReasonForContacting,
                                              related_name='reasons',
                                              on_delete=models.CASCADE)
    category = models.CharField(max_length=20,
                                choices=REASONS_FOR_CONTACTING.CHOICES)

    class Meta(object):
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __unicode__(self):
        try:
            return REASONS_FOR_CONTACTING.CHOICES_DICT[self.category]
        except KeyError:
            return self.category
