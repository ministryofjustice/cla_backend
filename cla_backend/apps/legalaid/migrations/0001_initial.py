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
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'legalaid', ['Category'])

        # Adding model 'Savings'
        db.create_table(u'legalaid_savings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('bank_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('investment_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('asset_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('credit_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'legalaid', ['Savings'])

        # Adding model 'PersonalDetails'
        db.create_table(u'legalaid_personaldetails', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('town', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mobile_phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('home_phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal(u'legalaid', ['PersonalDetails'])

        # Adding model 'EligibilityCheck'
        db.create_table(u'legalaid_eligibilitycheck', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('reference', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.Category'], null=True, blank=True)),
            ('your_savings', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='your_savings', null=True, to=orm['legalaid.Savings'])),
            ('partner_savings', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='partner_savings', null=True, to=orm['legalaid.Savings'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'legalaid', ['EligibilityCheck'])

        # Adding model 'Property'
        db.create_table(u'legalaid_property', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('value', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('equity', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('share', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('eligibility_check', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.EligibilityCheck'])),
        ))
        db.send_create_signal(u'legalaid', ['Property'])

        # Adding model 'Case'
        db.create_table(u'legalaid_case', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('reference', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('eligibility_check', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.EligibilityCheck'])),
            ('personal_details', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.PersonalDetails'])),
        ))
        db.send_create_signal(u'legalaid', ['Case'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'legalaid_category')

        # Deleting model 'Savings'
        db.delete_table(u'legalaid_savings')

        # Deleting model 'PersonalDetails'
        db.delete_table(u'legalaid_personaldetails')

        # Deleting model 'EligibilityCheck'
        db.delete_table(u'legalaid_eligibilitycheck')

        # Deleting model 'Property'
        db.delete_table(u'legalaid_property')

        # Deleting model 'Case'
        db.delete_table(u'legalaid_case')


    models = {
        u'legalaid.case': {
            'Meta': {'object_name': 'Case'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'eligibility_check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.EligibilityCheck']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'personal_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.PersonalDetails']"}),
            'reference': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'legalaid.category': {
            'Meta': {'ordering': "['order']", 'object_name': 'Category'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'legalaid.eligibilitycheck': {
            'Meta': {'object_name': 'EligibilityCheck'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'partner_savings': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'partner_savings'", 'null': 'True', 'to': u"orm['legalaid.Savings']"}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'your_savings': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'your_savings'", 'null': 'True', 'to': u"orm['legalaid.Savings']"})
        },
        u'legalaid.personaldetails': {
            'Meta': {'object_name': 'PersonalDetails'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'town': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'legalaid.property': {
            'Meta': {'object_name': 'Property'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'eligibility_check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.EligibilityCheck']"}),
            'equity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'share': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'legalaid.savings': {
            'Meta': {'object_name': 'Savings'},
            'asset_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'bank_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'credit_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['legalaid']