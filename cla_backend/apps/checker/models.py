from django.db import models
from django.db.models import Count
from model_utils.models import TimeStampedModel
from uuidfield import UUIDField

from cla_common.constants import REASONS_FOR_CONTACTING


class ReasonForContacting(TimeStampedModel):
    class analytics:
        _allow_analytics = True

    reference = UUIDField(auto=True, unique=True)
    other_reasons = models.TextField(blank=True)
    referrer = models.CharField(max_length=255, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    case = models.ForeignKey("legalaid.Case", blank=True, null=True)

    class Meta(object):
        verbose_name_plural = "reasons for contacting"
        ordering = ("-created",)

    @classmethod
    def get_category_stats(cls):
        # this is the method used by the checker admin page
        # refactored so can be used by the new reports method
        total_count, data = cls.get_all_categories()
        return cls.calc_category_stats(data, total_count)

    @classmethod
    def calc_category_stats(
        cls, category_data, reasons_for_contacting_count, start_date=None, end_date=None, referrer=None
    ):
        # known categories, preserving order
        categories = [
            {
                "key": choice[0],
                "description": choice[1],
                "count": category_data[choice[0]] if choice[0] in category_data else 0,
            }
            for choice in REASONS_FOR_CONTACTING.CHOICES
        ]
        # unknown categories (perhaps have been removed)
        for category, count in category_data.iteritems():
            if category not in REASONS_FOR_CONTACTING.CHOICES_DICT:
                categories.append({"key": category, "description": category, "count": count})
        # calculate percentage of all responses that chose each option
        percentage_total = 100.0 / reasons_for_contacting_count if reasons_for_contacting_count else 0.0

        filters = None
        if start_date and end_date:
            filters = models.Q(reason_for_contacting__created__gte=start_date) & models.Q(
                reason_for_contacting__created__lte=end_date
            )
        if referrer:
            filters = filters & models.Q(reason_for_contacting__referrer__endswith=referrer)

        qs = (
            ReasonForContactingCategory.objects.filter(reason_for_contacting__case__isnull=False)
            .values("category")
            .annotate(count=Count("*"))
        )
        if filters:
            qs = qs.filter(filters)
        categories_with_cases = {rfc_category["category"]: rfc_category["count"] for rfc_category in qs}

        qs = (
            ReasonForContactingCategory.objects.filter(reason_for_contacting__case__isnull=True)
            .values("category")
            .annotate(count=Count("*"))
        )
        if filters:
            qs = qs.filter(filters)
        categories_without_cases = {rfc_category["category"]: rfc_category["count"] for rfc_category in qs}

        for category in categories:
            category["with_cases"] = (
                categories_with_cases[category["key"]] if category["key"] in categories_with_cases else 0
            )
            category["without_cases"] = (
                categories_without_cases[category["key"]] if category["key"] in categories_without_cases else 0
            )
            category["percentage"] = round(category["count"] * percentage_total, 2)
        return dict(categories=categories, total_count=reasons_for_contacting_count)

    @classmethod
    def get_all_categories(cls):
        data = (
            ReasonForContactingCategory.objects.values_list("category")
            .annotate(count=models.Count("category"))
            .order_by()
        )
        data = dict(data)
        total_count = cls.objects.count()
        return total_count, data

    @classmethod
    def get_filtered_categories(cls, start_date, end_date, referrer=None):
        # there must be a start date and an end date
        if not start_date and end_date:
            raise ValueError("Must provide a start date and an end date")
        filters_count = models.Q(created__gte=start_date) & models.Q(created__lte=end_date)
        filters_data = models.Q(
            reason_for_contacting__created__lte=end_date, reason_for_contacting__created__gte=start_date
        )
        if referrer:
            filters_count &= models.Q(referrer__endswith=referrer)
            filters_data &= models.Q(reason_for_contacting__referrer__endswith=referrer)
        total_count = cls.objects.filter(filters_count).count()
        data = (
            ReasonForContactingCategory.objects.filter(filters_data)
            .values_list("category")
            .annotate(count=models.Count("category"))
            .order_by()
        )
        data = dict(data)
        return total_count, data

    @classmethod
    def get_report_category_stats(cls, start_date=None, end_date=None, referrer=None):
        # this returns limited results that can be downloaded as a report
        total_count, data = cls.get_filtered_categories(start_date, end_date, referrer)
        return cls.calc_category_stats(data, total_count, start_date, end_date, referrer)

    @classmethod
    def get_top_referrers(cls, count=8):
        total_count = cls.objects.count()
        percentage_total = 100.0 / total_count if total_count else 0.0
        data = cls.objects.values("referrer").annotate(count=models.Count("referrer")).order_by("-count", "referrer")
        return [
            {"referrer": item["referrer"], "percentage": item["count"] * percentage_total} for item in data[:count]
        ]

    @classmethod
    def get_top_report_referrers(cls, start_date, end_date, count=8):
        # how many objects in this time range?
        filter_date = models.Q(created__gte=start_date) & models.Q(created__lte=end_date)
        total_count = cls.objects.filter(filter_date).count()
        percentage_total = 100.0 / total_count if total_count else 0.0
        data = (
            cls.objects.filter(filter_date)
            .values("referrer")
            .annotate(count=models.Count("referrer"))
            .order_by("-count", "referrer")
        )
        return [
            {"referrer": item["referrer"], "percentage": item["count"] * percentage_total} for item in data[:count]
        ]

    @property
    def reason_categories(self):
        if self.reasons.count():
            return u", ".join(map(unicode, self.reasons.all()))
        return u"(No categories specified)"

    def __unicode__(self):
        reason_count = self.reasons.count()
        description = u"%d reasons" % reason_count if reason_count else u"No reasons specified"
        if self.case:
            return description + u" (Case: %s)" % self.case.reference
        return description


class ReasonForContactingCategory(models.Model):
    class analytics:
        _allow_analytics = True

    reason_for_contacting = models.ForeignKey(ReasonForContacting, related_name="reasons", on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=REASONS_FOR_CONTACTING.CHOICES)

    class Meta(object):
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __unicode__(self):
        try:
            return REASONS_FOR_CONTACTING.CHOICES_DICT[self.category]
        except KeyError:
            return self.category
