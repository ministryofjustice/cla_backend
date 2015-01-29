from django.db import DEFAULT_DB_ALIAS
import south


class FakeFirstMigration(object):
    def __init__(self, *args, **kwargs):
        self.forwards, self._forwards = self._forwards, self.forwards
        super(FakeFirstMigration, self).__init__(*args, **kwargs)

    def tables_already_exist(self, orm, database=DEFAULT_DB_ALIAS):
        conn = south.db.dbs[database]._get_connection()
        tables = conn.introspection.table_names()

        # Find out if the migration has tables:
        for label, model in orm.models.items():
            if label.split('.')[0] not in self.complete_apps:
                continue
            if model._meta.db_table in tables:
                return True
        return False

    def _forwards(self, orm):
        if not self.tables_already_exist(orm):
            super(FakeFirstMigration, self)._forwards(orm)
