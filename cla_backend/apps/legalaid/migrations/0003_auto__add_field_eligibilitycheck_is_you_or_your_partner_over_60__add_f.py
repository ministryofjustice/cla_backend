# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'EligibilityCheck.is_you_or_your_partner_over_60'
        db.add_column(u'legalaid_eligibilitycheck', 'is_you_or_your_partner_over_60',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'EligibilityCheck.has_partner'
        db.add_column(u'legalaid_eligibilitycheck', 'has_partner',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'EligibilityCheck.is_you_or_your_partner_over_60'
        db.delete_column(u'legalaid_eligibilitycheck', 'is_you_or_your_partner_over_60')

        # Deleting field 'EligibilityCheck.has_partner'
        db.delete_column(u'legalaid_eligibilitycheck', 'has_partner')


    models = {
        u'legalaid.case': {
            'Meta': {'object_name': 'Case'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'eligibility_check': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['legalaid.EligibilityCheck']", 'unique': 'True'}),
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
            'dependants_old': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'dependants_young': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'has_partner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_you_or_your_partner_over_60': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'partner_finances': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'partner_savings'", 'null': 'True', 'to': u"orm['legalaid.Finance']"}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'your_finances': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'your_savings'", 'null': 'True', 'to': u"orm['legalaid.Finance']"}),
            'your_problem_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'legalaid.finance': {
            'Meta': {'object_name': 'Finance'},
            'asset_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'bank_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'credit_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'earnings': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_balance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'other_income': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'self_employed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        }
    }

    complete_apps = ['legalaid']