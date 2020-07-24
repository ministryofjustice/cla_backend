"""
Build a django json fixture from the CSV export of the Knowledgebase spreadsheet.
"""
import csv
import json
import sys
from datetime import datetime
from django.utils import timezone


class KnowledgebaseCsvParse(object):
    def __init__(self, csv_file_handle):

        self.datetime_now = datetime.now().replace(tzinfo=timezone.get_current_timezone()).isoformat()

        #                        csv_field -> django_field_name
        #                        only include fields which are used
        self.field_mapping = {
            "Organisation/Umbrella": "organisation",
            "Service (name resource will be given on KB)": "service_name",
            "When to use (N.B. for in scope categories, signpost using directory in first instance).": "when_to_use",
            "Entry type": "resource_type",
            "Description": "description",
            "Type of service/client group": "type_of_service",
            "Guidance": "how_to_use",
            # <ArticleCategory>
            "Debt": "Debt",
            "Education": "Education",
            "Discrimination": "Discrimination",
            "Housing": "Housing",
            "Family": "Family",
            "Welfare Benefits": "Welfare benefits",
            "AAP": "Action against police",
            "Clin Neg": "Clinical negligence",
            "Comm Care": "Community care",
            "Consumer": "Consumer",
            "Crime": "Crime",
            "Employment": "Employment",
            "Immig & Ass": "Immigration and asylum",
            "MH": "Mental health",
            "Misc": "Miscellaneous",
            "PI": "Personal injury",
            "Public": "Public",
            "Generic": "Generic",
            # </ArticleCategory>
            "Helpline": "helpline",
            "Website": "website",
            "Address": "address",
            "Opening Hours": "opening_hours",
            "Coverage": "geographic_coverage",
            "Accessibility": "accessibility",
            "Current keywords": "keywords",
        }

        dialect = csv.Sniffer().sniff(csv_file_handle.read(1024))
        csv_file_handle.seek(0)

        self.csv_reader = csv.DictReader(csv_file_handle, dialect=dialect)
        self.fields = [f for f in self.csv_reader.fieldnames]

        self.csv_article_category_fields = [
            "Debt",
            "Education",
            "Discrimination",
            "Housing",
            "Family",
            "Welfare Benefits",
            "AAP",
            "Clin Neg",
            "Comm Care",
            "Consumer",
            "Crime",
            "Employment",
            "Immig & Ass",
            "MH",
            "Misc",
            "PI",
            "Public",
            "Generic",
        ]
        self._check_csv_fields()

    def _check_csv_fields(self):
        """
        ensure the CSV files has all the required fields. Bomb with an
        error message if not.
        """
        # in field_mapping but not in csv's 'fields'
        diff = list(set(self.field_mapping.keys()).difference(set(self.fields)))

        for missing_field in diff:
            self.log("Expected field '%s' missing from CSV and is needed" % missing_field)

        if len(diff) > 0:
            sys.exit(-1)

    def _article_category_fixture(self):
        """
        @return: tuple of    list of dictionaries ready for serialising into fixture
                          +  lookup dictionary of CSV field name -> DB's ArticleCategory pk
        """
        fixture = []
        article_category_lookup = {}
        position = 0
        for ac_field in self.csv_article_category_fields:
            position += 1
            d = {
                "pk": position,
                "model": "knowledgebase.articlecategory",
                "fields": {
                    "name": self.field_mapping[ac_field],
                    "created": self.datetime_now,
                    "modified": self.datetime_now,
                },
            }
            fixture.append(d)
            article_category_lookup[ac_field] = position
        return fixture, article_category_lookup

    def fixture_as_json(self):
        """
        @return: String of complete JSON doc. with all three record types.
        """

        fixture = []
        ac_fixture, article_category_lookup = self._article_category_fixture()
        fixture.extend(ac_fixture)

        stats = {"skipped": 0, "loaded": 0}
        position = 0
        for r in self.csv_reader:
            if r["Entry type"] != "Other resource for clients" and r["Entry type"] != "Legal resource for clients":
                stats["skipped"] += 1
                continue

            stats["loaded"] += 1
            record_categories = {}
            position += 1
            d = {
                "pk": position,
                "model": "knowledgebase.article",
                "fields": {"created": self.datetime_now, "modified": self.datetime_now},
            }
            for csv_field, django_field_name in self.field_mapping.iteritems():

                if csv_field in self.csv_article_category_fields:
                    # these are the ArticleCategory related fields
                    record_categories[csv_field] = r[csv_field]

                elif django_field_name == "resource_type":
                    d["fields"][django_field_name] = r[csv_field][:5].upper()

                elif django_field_name == "website":

                    website = r[csv_field].decode("ascii", "ignore")
                    if not website.startswith("http"):
                        website = "http://" + website

                    d["fields"][django_field_name] = website

                else:
                    # normal field
                    d["fields"][django_field_name] = r[csv_field].decode("ascii", "ignore")

            fixture.append(d)

            article_category_maxtrix_records = self.create_article_category_maxtrix(
                record_categories, position, article_category_lookup
            )
            fixture.extend(article_category_maxtrix_records)

        #             record_category_object = RecordCategoryObjects()
        #             record_category_object.create_article_category_maxtrix(
        #                 record_categories, self.datetime_now, position, article_category_lookup, self.log
        #             )
        #             fixture.extend(record_category_object.records)

        # TODO
        # Finish writing functionality as a class

        for stat, s_count in stats.iteritems():
            self.log("%s records %s" % (s_count, stat))

        return json.dumps(fixture, indent=4)

    def log(self, msg):
        sys.stderr.write(msg + "\n")

    def create_article_category_maxtrix(self, record_categories, position, article_category_lookup):
        records = []
        for article_cat_position, (csv_field, spreadsheet_value) in enumerate(record_categories.iteritems()):
            if len(spreadsheet_value) > 0:
                if spreadsheet_value != "x" and not spreadsheet_value.startswith("Preferred"):
                    self.log("Odd value %s in %s" % (spreadsheet_value, csv_field))
                    continue
                d = {
                    "pk": article_cat_position,
                    "model": "knowledgebase.articlecategorymatrix",
                    "fields": {
                        "created": self.datetime_now,
                        "modified": self.datetime_now,
                        "article": position,
                        "article_category": article_category_lookup[csv_field],
                        "preferred_signpost": spreadsheet_value.startswith("Preferred"),
                    },
                }
                records.append(d)
        return records
