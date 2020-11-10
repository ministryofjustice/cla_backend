# coding=utf-8
import logging
from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min
from django.utils.timezone import now
from cla_eventlog.models import Log

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "LGA-294 specific monitoring command. Alert when multiple outcome codes "
        "that should only occur once are found for today (since 00:00)"
    )

    def handle(self, *args, **options):
        self.stdout.write("Checking for multiple outcome codes")
        self.check_for_multiple_outcome_codes()

    @staticmethod
    def check_for_multiple_outcome_codes():
        # Outcome codes defined to appear only once on a case:
        # https://docs.google.com/spreadsheets/d/1hN64bA_H2a_0eC_5-k-0IY2-RKbCor2VGflp1ykQGa0/
        start_of_today = now().replace(hour=0, minute=0, second=0, microsecond=0)
        once_only_codes = [
            "PCB",
            "COPE",
            "DUPL",
            "MRNB",
            "NCOE",
            "DESP",
            "DECL",
            "MRCC",
            "NRES",
            "CPTA",
            "COSPF",
            "SPFM",
            "SPFN",
            "DREFER",
            "COI",
            "CLSP",
            "MANALC",
            "MANREF",
            "MIS",
            "MIS-MEANS",
            "MIS-OOS",
            "REF-EXT",
            "REF-INT",
            "REFSP",
            "REOPEN",
            "SPOR",
            "WROF",
        ]

        once_only_events_today = Log.objects.filter(created__gte=start_of_today, code__in=once_only_codes)
        once_only_codes_today = once_only_events_today.only("case__reference", "code", "created")
        once_only_codes_today_counts = once_only_codes_today.values("case__reference", "code").annotate(
            total=Count("code"), earliest=Min("created"), latest=Max("created")
        )
        multiple_codes_today = once_only_codes_today_counts.filter(total__gt=1).order_by("-total")

        if multiple_codes_today.exists():
            for i in multiple_codes_today:
                logger.warning("LGA-294 investigation. Multiple outcome codes today for case: {}".format(i))
        else:
            logger.info("LGA-294 No multiple outcome codes found for today")
