# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CaseArchived'
        db.create_table(u'historic_casearchived', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('full_name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('laa_reference', self.gf('django.db.models.fields.BigIntegerField')(unique=True, null=True, blank=True)),
            ('specialist_referred_to', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date_specialist_referred', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_specialist_closed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('knowledgebase_items_used', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('area_of_law', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('in_scope', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('financially_eligible', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('outcome_code', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('outcome_code_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'historic', ['CaseArchived'])


    def backwards(self, orm):
        # Deleting model 'CaseArchived'
        db.delete_table(u'historic_casearchived')


    models = {
        u'historic.casearchived': {
            'Meta': {'object_name': 'CaseArchived'},
            'area_of_law': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_specialist_closed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_specialist_referred': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'financially_eligible': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_scope': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'knowledgebase_items_used': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'laa_reference': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'outcome_code': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'outcome_code_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'specialist_referred_to': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['historic']