# coding=utf-8
import logging
from datetime import datetime, time
from itertools import groupby

import boto
from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from pytz import UTC

from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from cla_eventlog.models import Log
from reports.utils import get_s3_connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "LGA-125 specific command. Remove same day consecutive outcome codes."

    def handle(self, *args, **options):
        self.remove_same_day_consecutive_outcome_codes()

    def remove_same_day_consecutive_outcome_codes(self):
        logger.info("\nLGA-125: start remove_same_day_consecutive_outcome_codes {}".format(now()))

        # Older Django sans TruncDate, etc.
        outcome_events = (
            Log.objects.filter(type=LOG_TYPES.OUTCOME, level=LOG_LEVELS.HIGH)
            .extra(select={"day": "date( cla_eventlog_log.created )"})
            .values("case__reference", "code", "day")
        )

        # First pass. Gather case/day/code with >1 occurrences
        cases_with_daily_multiple_events = []
        grouped_results = groupby(outcome_events, key=lambda i: i)
        for (result, g) in grouped_results:
            count = sum(1 for _ in g)
            if count > 1:
                result["count"] = count
                cases_with_daily_multiple_events.append(result)

        # Second pass to reverse chronological scan through all log events for a case on a given day
        # Remove log events where an immediately earlier outcome code is the same
        same_day_consecutive_outcome_log_ids = set()

        for e in cases_with_daily_multiple_events:
            start_of_day = datetime.combine(e["day"], time.min).replace(tzinfo=UTC)
            eod_of_day = datetime.combine(e["day"], time.max).replace(tzinfo=UTC)
            case_outcomes_for_day = Log.objects.filter(
                case__reference=e["case__reference"],
                type=LOG_TYPES.OUTCOME,
                created__gte=start_of_day,
                created__lte=eod_of_day,
            ).order_by("-created")

            n = case_outcomes_for_day.count()
            logger.info(
                "\nLGA-125: Case {} outcome log ids for {}: {}".format(
                    e["case__reference"], e["day"], case_outcomes_for_day.values_list("id", flat=True)
                )
            )
            for index, event in enumerate(case_outcomes_for_day):
                # If there is an immediately previous outcome event on the same day and the code is the same,
                #   consider our event a dupe, and note its id for deletion
                if index < n - 1 and case_outcomes_for_day[index + 1].code == event.code:
                    same_day_consecutive_outcome_log_ids.add(event.id)
                    logger.info("LGA-125: {:<7} {:<7} remove: {}".format(event.id, event.code, event.created))
                else:
                    logger.info("LGA-125: {:<7} {:<7} keep:   {}".format(event.id, event.code, event.created))

        if same_day_consecutive_outcome_log_ids:
            dupes_to_remove = Log.objects.filter(id__in=same_day_consecutive_outcome_log_ids)
            try:
                self.write_queryset_to_s3(dupes_to_remove)
            except boto.exception.S3ResponseError as e:
                logger.error(
                    "LGA-125: Could not get bucket {}: {}".format(settings.AWS_DELETED_OBJECTS_BUCKET_NAME, e)
                )
            else:
                dupes_to_remove.delete()
                logger.info("LGA-125: Removed dupe Logs with ids: {}".format(same_day_consecutive_outcome_log_ids))
        else:
            logger.info("LGA-125: No dupe logs to remove")

    def write_queryset_to_s3(self, queryset):
        bucket = self.get_or_create_s3_bucket()
        key = bucket.new_key("deleted-log-objects-{}".format(now().isoformat()))
        serialized_queryset = serializers.serialize("json", queryset)
        key.set_contents_from_string(serialized_queryset)
        # Restore with:
        # for restored_log_object in serializers.deserialize('json', serialized_queryset):
        #     restored_log_object.save()

    @staticmethod
    def get_or_create_s3_bucket():
        conn = get_s3_connection()
        bucket_name = settings.AWS_DELETED_OBJECTS_BUCKET_NAME
        try:
            return conn.get_bucket(bucket_name)
        except boto.exception.S3ResponseError:
            conn.create_bucket(bucket_name, location=settings.AWS_S3_REGION_NAME)
            return conn.get_bucket(bucket_name)
