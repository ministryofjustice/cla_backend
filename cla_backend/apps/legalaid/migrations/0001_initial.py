# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'legalaid_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('raw_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'legalaid', ['Category'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'legalaid_category')


    models = {
        u'legalaid.category': {
            'Meta': {'ordering': "['order']", 'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'raw_description': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['legalaid']
