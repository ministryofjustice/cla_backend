# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'CaseArchived', fields ['full_name', 'date_of_birth', 'postcode', 'laa_reference', 'specialist_referred_to', 'date_specialist_referred', 'date_specialist_closed', 'knowledgebase_items_used', 'area_of_law', 'in_scope', 'financially_eligible', 'outcome_code', 'outcome_code_date']
        db.create_index(u'historic_casearchived', ['full_name', 'date_of_birth', 'postcode', 'laa_reference', 'specialist_referred_to', 'date_specialist_referred', 'date_specialist_closed', 'knowledgebase_items_used', 'area_of_law', 'in_scope', 'financially_eligible', 'outcome_code', 'outcome_code_date'])


    def backwards(self, orm):
        # Removing index on 'CaseArchived', fields ['full_name', 'date_of_birth', 'postcode', 'laa_reference', 'specialist_referred_to', 'date_specialist_referred', 'date_specialist_closed', 'knowledgebase_items_used', 'area_of_law', 'in_scope', 'financially_eligible', 'outcome_code', 'outcome_code_date']
        db.delete_index(u'historic_casearchived', ['full_name', 'date_of_birth', 'postcode', 'laa_reference', 'specialist_referred_to', 'date_specialist_referred', 'date_specialist_closed', 'knowledgebase_items_used', 'area_of_law', 'in_scope', 'financially_eligible', 'outcome_code', 'outcome_code_date'])


    models = {
        u'historic.casearchived': {
            'Meta': {'object_name': 'CaseArchived', 'index_together': "[['full_name', 'date_of_birth', 'postcode', 'laa_reference', 'specialist_referred_to', 'date_specialist_referred', 'date_specialist_closed', 'knowledgebase_items_used', 'area_of_law', 'in_scope', 'financially_eligible', 'outcome_code', 'outcome_code_date']]"},
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