from collections import defaultdict
import csv
import datetime
from optparse import make_option

from dateutil.parser import parse
from django.core.management.base import BaseCommand
from django.utils.itercompat import is_iterable
from django.utils.timezone import make_aware, UTC

from historic.models import CaseArchived


def yesno(str):
    return True if str.upper() == "YES" else False


def parse_dt(str):
    str = str.strip()
    if str and is_iterable(str):
        try:
            return make_aware(parse(str, dayfirst=True), UTC())
        except Exception:
            import pdb

            pdb.set_trace()


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option("-c", "--case_file", dest="case_file", help="path to historic cases .csv file"),
        make_option("-k", "--kb_file", dest="kb_file", help="path to accompanying knowledge-base .csv file"),
    )

    help = "Create CaseArchived object from a case and knowledge-base CSV"

    required_args = ("case_file", "kb_file")

    def handle(self, *args, **options):
        if options["case_file"] is None or options["kb_file"] is None:
            raise ValueError("Missing parameter. Try --help")
        # Load referrals
        self.stderr.write("Loading referrals from %s" % options["kb_file"])
        self.load_referrals(options["kb_file"])
        self.stderr.write("Found referrals %s for cases" % len(self.referrals))

        # Load cases
        self.stderr.write("Loading cases from %s" % options["case_file"])
        self.load_cases(options["case_file"])
        self.stderr.write("Found %s cases" % len(self.cases))

        # Clear out existing cases if required
        existing_cases_count = CaseArchived.objects.all().count()
        if existing_cases_count:
            self.stderr.write("Clearing out %s existing historic cases." % existing_cases_count)
            CaseArchived.objects.all().delete()

        fake_datetime = datetime.datetime(1900, 1, 1).replace(tzinfo=UTC())
        # Writing Cases to the database

        def _getdate(x):
            return x.outcome_code_date or fake_datetime

        self.cases = sorted(self.cases, key=_getdate, reverse=True)

        CaseArchived.objects.bulk_create(self.cases)

    def get_referrals(self, laa_reference):
        all_refs = self.referrals.get(laa_reference)
        if all_refs:
            return "\n".join(all_refs)

    def load_referrals(self, filename):
        def _decode_legacy(value):
            if isinstance(value, bytes):
                return value.decode("ISO-8859-1")
            return value

        self.referrals = defaultdict(list)
        with open(filename, "r", newline="") as f:
            reader = csv.DictReader(f)
            for count, row in enumerate(reader):
                if count % 20 == 0:
                    self.stderr.write(".", ending="")
                self.referrals[row["CaseID"]].append(_decode_legacy(row["Title"]))

    def load_cases(self, filename):
        def _decode_legacy(value):
            if isinstance(value, bytes):
                return value.decode("ISO-8859-1")
            return value

        def record_to_case_archived(row):
            full_name = row["FirstName"] + " " + row["Surname"]
            case = CaseArchived(
                full_name=_decode_legacy(full_name),
                date_of_birth=parse_dt(row["DateOfBirth"]),
                postcode=_decode_legacy(row["PostCode"]),
                laa_reference=row["CaseID"],
                created=parse_dt(row["DateCreated"]),
                outcome_code=_decode_legacy(row["OutcomeCode"]),
                outcome_code_date=parse_dt(row["OutcomeDate"]),
                specialist_referred_to=_decode_legacy(row["SpecialistReferred"]),
                date_specialist_referred=parse_dt(row["DateSpecialistClosed"]),
                area_of_law=_decode_legacy(row["AreaOfLaw"]),
                in_scope=yesno(row["IsInScope"]),
                financially_eligible=bool(row["Eligible"]),
                knowledgebase_items_used=self.get_referrals(row["CaseID"]),
            )

            search_field = []
            for field in ["full_name", "postcode", "laa_reference", "outcome_code"]:
                val = getattr(case, field)
                if val:
                    search_field.append(val.upper())
            case.search_field = " ".join(search_field)

            return case

        self.cases = []
        with open(filename, "r", newline="") as f:
            reader = csv.DictReader(f, lineterminator="\n")
            for count, row in enumerate(reader):
                if count % 20 == 0:
                    self.stderr.write(".", ending="")
                self.cases.append(record_to_case_archived(row))
