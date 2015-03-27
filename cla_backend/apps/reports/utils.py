import os
import tempfile
import glob
import zipfile
import shutil
from datetime import datetime, date, time, timedelta

from django.db import connection

from legalaid.utils import diversity


class OBIEEExporter(object):
    basic_sql_files = [
        'export_auth_user.sql',
        'export_call_centre_operator.sql',
        'export_diagnosis_diagnosis_traversal.sql',
        'export_event_log_log.sql',
        'export_knowledge_base_article.sql',
        'export_knowledge_base_article_category.sql',
        'export_knowledge_base_article_category_matrix.sql',
        'export_legal_aid_adaptationdetails.sql',
        'export_legal_aid_call_centre_operator.sql',
        'export_legal_aid_case.sql',
        'export_legal_aid_case_knowledge_base_assignment.sql',
        'export_legal_aid_category.sql',
        'export_legal_aid_deductions.sql',
        'export_legal_aid_eligibility_check.sql',
        'export_legal_aid_income.sql',
        'export_legal_aid_matter_type.sql',
        'export_legal_aid_media_code.sql',
        'export_legal_aid_person.sql',
        'export_legal_aid_property.sql',
        'export_legal_aid_savings.sql',
        'export_legal_aid_third_party_details.sql',
        'export_provider_csv_upload.sql',
        'export_provider_feedback.sql',
        'export_provider_out_of_hours_rota.sql',
        'export_provider_provider.sql',
        'export_provider_provider_allocation.sql',
        'export_provider_staff.sql',
        'export_timer_timer.sql',
    ]

    no_timestamp_sql_files = [
        'export_auth_group.sql',
        'export_auth_user_groups.sql',
        'export_media_code_group.sql',
    ]

    personal_details_sql_file = 'export_legal_aid_personaldetails.sql'
    sql_path = os.path.join(os.path.dirname(__file__), 'sql', 'obiee')

    filename = 'cla_database.zip'

    def __init__(self, export_path, passphrase, dt_from=None, dt_to=None):
        self.export_path = export_path
        self.passphrase = passphrase
        self.dt_from = dt_from or (
            (datetime.combine(date.today(), time.min)
                - timedelta(days=1)).isoformat()
        )
        self.dt_to = dt_to or (
            datetime.combine(date.today(), time.min).isoformat()
        )
        self.tmp_export_path = tempfile.mkdtemp()

    def export(self):
        self.export_basic_tables()
        self.export_no_timestamp_tables()
        self.export_personal_details()

        self.generate_zip()

    def export_basic_tables(self):
        for sql in self.basic_sql_files:
            sql_path = os.path.join(self.sql_path, sql)
            with open(sql_path, 'r') as f:
                query = f.read()

            csv_filename = self.csv_filename_from_sql_path(sql_path)
            args = [self.dt_from, self.dt_to]

            self.execute_csv_export(csv_filename, query, args)

    def export_no_timestamp_tables(self):
        for sql in self.no_timestamp_sql_files:
            sql_path = os.path.join(self.sql_path, sql)
            with open(sql_path, 'r') as f:
                query = f.read()

            csv_filename = self.csv_filename_from_sql_path(sql_path)

            self.execute_csv_export(csv_filename, query)

    def export_personal_details(self):
        sql_path = os.path.join(self.sql_path, self.personal_details_sql_file)
        with open(sql_path, 'r') as f:
            query = f.read()
            de = "pgp_pub_decrypt(diversity, dearmor('{key}'), %s)::json".\
                format(
                    key=diversity.get_private_key()
                )
            query = query.format(diversity_expression=de)

        csv_filename = self.csv_filename_from_sql_path(
            self.personal_details_sql_file)
        args = [self.passphrase, self.dt_from, self.dt_to]

        self.execute_csv_export(csv_filename, query, args)

    def execute_csv_export(self, filename, query, args=None):
        if not args:
            args = []

        with open(os.path.join(self.tmp_export_path, filename), 'w') as d:
            cursor = connection.cursor()
            q = cursor.mogrify(query, args)
            cursor.copy_expert(q, d)
            cursor.close()

    def csv_filename_from_sql_path(self, filename):
        filename = filename.split('/')[-1]
        return filename.replace('export_', '').replace('.sql', '.csv')

    def generate_zip(self):
        os.chdir(self.tmp_export_path)
        with open(self.filename, 'w+b') as zp:
            with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
                for f in glob.glob('*.csv'):
                    z.write(f)
        shutil.move('%s/%s' % (self.tmp_export_path, self.filename),
                    '%s/%s' % (self.export_path, self.filename))
        shutil.rmtree(self.tmp_export_path)
