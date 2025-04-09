import datetime
from datetime import timedelta
from django.db import models
from django.db.models import Count
from django.utils import timezone
from extended_choices import Choices
from model_utils.models import TimeStampedModel
from uuidfield import UUIDField
from jsonfield import JSONField
from cla_common.constants import REASONS_FOR_CONTACTING, CALLBACK_TYPES
from cla_common.call_centre_availability import SLOT_INTERVAL_MINS
from core.cloning import CloneModelMixin

# These are all the possible start times for a callback slot,
# a slot has a duration of 30 minutes.
CALLBACK_TIME_SLOTS = Choices(
    # constant, db_id, friendly string
    ("NINE_AM", "0900", "09:00-09:30"),
    ("HALF_NINE_AM", "0930", "09:30-10:00"),
    ("TEN_AM", "1000", "10:00-10:30"),
    ("HALF_TEN_AM", "1030", "10:30-11:00"),
    ("ELEVEN_AM", "1100", "11:00-11:30"),
    ("HALF_ELEVEN_AM", "1130", "11:30-12:00"),
    ("TWELVE_AM", "1200", "12:00-12:30"),
    ("HALF_TWELVE_AM", "1230", "12:30-13:00"),
    ("ONE_PM", "1300", "13:00-13:30"),
    ("HALF_ONE_PM", "1330", "13:30-14:00"),
    ("TWO_PM", "1400", "14:00-14:30"),
    ("HALF_TWO_PM", "1430", "14:30-15:00"),
    ("THREE_PM", "1500", "15:00-15:30"),
    ("HALF_THREE_PM", "1530", "15:30-16:00"),
    ("FOUR_PM", "1600", "16:00-16:30"),
    ("HALF_FOUR_PM", "1630", "16:30-17:00"),
    ("FIVE_PM", "1700", "17:00-17:30"),
    ("HALF_FIVE_PM", "1730", "17:30-18:00"),
    ("SIX_PM", "1800", "18:00-18:30"),
    ("HALF_SIX_PM", "1830", "18:30-19:00"),
    ("SEVEN_PM", "1900", "19:00-19:30"),
    ("HALF_SEVEN_PM", "1930", "19:30-20:00"),
)


class ReasonForContacting(TimeStampedModel):
    class Analytics:
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
    class Analytics:
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


class CallbackTimeSlot(TimeStampedModel):
    """
    Represents a time slot a user can request a call back from the call centre.
    If the slot exists then it will limit the number of the call backs that can be scheduled from the time slot.
    If the slot does not exist then an unlimited number of callbacks can be scheduled for that time slot.

    The callback slots are set via a CSV Upload in the form:
    date, start_time, capacity

    Args:
        date (date): The date of the callback
        time (TextField)
    """

    time = models.CharField(max_length=4, choices=CALLBACK_TIME_SLOTS.CHOICES)
    date = models.DateField()
    capacity = models.IntegerField()

    @property
    def remaining_capacity(self):
        return self.get_remaining_capacity_by_range(
            self.capacity, self.callback_start_datetime(), self.callback_end_datetime()
        )

    @staticmethod
    def get_model_from_datetime(dt, fallback_to_previous_week=True):
        assert isinstance(dt, datetime.datetime)
        is_fallback = False
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        model = CallbackTimeSlot.objects.filter(date=dt.date(), time=dt.strftime("%H%M")).first()

        if not model and fallback_to_previous_week:
            previous_week = dt - datetime.timedelta(weeks=1)
            model = CallbackTimeSlot.objects.filter(
                date=previous_week.date(), time=previous_week.strftime("%H%M")
            ).first()
            is_fallback = True

        return is_fallback, model

    @staticmethod
    def get_time_from_interval_string(interval):
        dt = datetime.datetime.strptime(interval, "%H%M")
        return dt.time()

    @staticmethod
    def is_threshold_breached_on_date(dt):
        """
        This function checks if there are any remaining slots available in a day
        and returns True if there are none. This works from current time in case
        of previous slots

        If a callback slot has not been defined, it will default the capacity to
        False to prevent alerting emails being sent every time someone books on a day
        with unlimited capacity as per business requirement
        """
        for slot_time in CALLBACK_TIME_SLOTS.CHOICES:
            time = CallbackTimeSlot.get_time_from_interval_string(slot_time[0])
            slot_dt = datetime.datetime.combine(dt.date(), time)
            _, slot = CallbackTimeSlot.get_model_from_datetime(slot_dt)
            # Undefined Slot
            if slot is None:
                return False
            if slot_dt >= (datetime.datetime.now() + timedelta(hours=2)):
                if slot.remaining_capacity > 0:
                    return False
        return True

    @staticmethod
    def get_remaining_capacity_by_range(capacity, start_dt, end_dt):
        from legalaid.models import Case

        # otherwise this will match cases that have a requires_action_at of the end date(don't want it to be inclusive)
        end_dt = end_dt - datetime.timedelta(seconds=1)
        count = Case.objects.filter(
            requires_action_at__range=(start_dt, end_dt), callback_type=CALLBACK_TYPES.CHECKER_SELF
        ).count()
        return capacity - count

    def callback_start_datetime(self):
        dt = datetime.datetime.combine(self.date, self.get_time_from_interval_string(self.time))
        return timezone.make_aware(dt)

    def callback_end_datetime(self):
        return self.callback_start_datetime() + datetime.timedelta(minutes=SLOT_INTERVAL_MINS)


class ScopeTraversal(CloneModelMixin, TimeStampedModel):
    """ Stores the information about the users journey through Check if you can get Legal Aid. """

    class Analytics:
        _allow_analytics = True

    FINANCIAL_ASSESSMENT_STATUSES = Choices(
        # constant, db_id, display string
        ("PASSED", "PASSED", "Passed"),
        ("FAILED", "FAILED", "Failed"),
        ("FAST_TRACK", "FAST_TRACK", "Client told to call the helpline for the assessment."),
        # Operationally fast tracked due the client indicating they are at risk of harm, are under 18, have trapped capital etc.
        ("SKIPPED", "SKIPPED", "No details. Client called the helpline directly.")
        # The client skipped the financial assessment due to clicking "Contact Us" directly.
    )

    FAST_TRACK_REASON = Choices(
        # constant, db_id, display string
        ("HARM", "HARM", "User has indicated they are at risk of harm"),
        ("MORE_INFO_REQUIRED", "MORE_INFO_REQUIRED", "Further scoping information is required"),
        ("OTHER", "OTHER", "Other"),
    )

    scope_answers = JSONField(default=dict)
    category = JSONField(default=dict)  # {"name": Category display name, "chs_code": Category name code}
    subcategory = JSONField(default=dict)  # {"name": Subcategory Name, "description": Subcategory description}
    financial_assessment_status = models.CharField(null=True, max_length=32, choices=FINANCIAL_ASSESSMENT_STATUSES)
    fast_track_reason = models.CharField(null=True, max_length=32, choices=FAST_TRACK_REASON)
    reference = UUIDField(auto=True, unique=True)

    cloning_config = {"excludes": ["created", "modified"]}
