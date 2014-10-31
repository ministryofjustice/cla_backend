from collections import defaultdict
import csv
from django.utils.itercompat import is_iterable
from historic.models import CaseArchived
import os
import sys
from optparse import make_option
from dateutil.parser import parse
from django.utils.timezone import make_aware, UTC



from django.core.management.base import BaseCommand

def yesno(str):
    return True if str.upper() == 'YES' else False

def parse_dt(str):
    str = str.strip()
    if str and is_iterable(str):
        try:
            return make_aware(parse(str, dayfirst=True), UTC())
        except Exception as e:
            import pdb; pdb.set_trace()



class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-c','--case_file',
                    dest='case_file',
                    help='path to historic cases .csv file'
        ),
        make_option('-k','--kb_file',
                    dest='kb_file',
                    help='path to accompanying knowledge-base .csv file'
        ),
    )

    help = ('Create CaseArchived object from a case and knowledge-base CSV')

    required_args = (
        'case_file',
        'kb_file'
    )

    def handle(self, *args, **options):
        if options['case_file'] is None or options['kb_file'] is None:
            raise ValueError('Missing parameter. Try --help')
        # Load referrals
        self.stderr.write('Loading referrals from %s' % options['kb_file'])
        self.load_referrals(options['kb_file'])
        self.stderr.write('Found referrals %s for cases' % len(self.referrals))


        # Load cases
        self.stderr.write('Loading cases from %s' % options['case_file'])
        self.load_cases(options['case_file'])
        self.stderr.write('Found %s cases' % len(self.cases))

        # Clear out existing cases if required
        existing_cases_count = CaseArchived.objects.all().count()
        if existing_cases_count:
            self.stderr.write('Clearing out %s existing historic cases.' % existing_cases_count)
            CaseArchived.objects.all().delete()

        # Writing Cases to the database
        CaseArchived.objects.bulk_create(self.cases)


    def get_referrals(self, laa_reference):
        all_refs = self.referrals.get(laa_reference)
        if all_refs:
            return '\n'.join(all_refs)

    def load_referrals(self, filename):
        self.referrals = defaultdict(list)
        with open(filename, 'rU') as f:
            reader = csv.DictReader(f)
            for count, row in enumerate(reader):
                if count % 20 == 0:
                    self.stderr.write('.', ending='')
                self.referrals[row['CaseID']].append(unicode(row['Title'], "ISO-8859-1"))


    def load_cases(self, filename):

        def record_to_case_archived(row):
            full_name = row['FirstName'] + row['Surname']
            return CaseArchived(
                full_name=unicode(full_name, "ISO-8859-1"),
                date_of_birth=parse_dt(row['DOB']),
                postcode=unicode(row['PostCode'], "ISO-8859-1"),
                laa_reference=row['CaseID'],
                created=parse_dt(row['DateCreated']),
                outcome_code=unicode(row['OutcomeCode'], "ISO-8859-1"),
                outcome_code_date=parse_dt(row['OutcomeDate']),
                specialist_referred_to=unicode(row['SpecialistReferred'], "ISO-8859-1"),
                date_specialist_referred=parse_dt(row['DateSpecialistClosed']),
                area_of_law=unicode(row['AreaOfLaw'], "ISO-8859-1"),
                in_scope=yesno(row['IsInScope']),
                financially_eligible=bool(row['Eligible']),
                knowledgebase_items_used=self.get_referrals(row['CaseID'])
            )

        self.cases = []
        with open(filename, 'rU') as f:
            reader = csv.DictReader(f, lineterminator='\n')
            for count, row in enumerate(reader):
                if count % 20 == 0:
                    self.stderr.write('.', ending='')
                self.cases.append(record_to_case_archived(row))
