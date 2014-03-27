# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Case.personal_details'
        db.alter_column(u'legalaid_case', 'personal_details_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.PersonalDetails'], null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Case.personal_details'
        raise RuntimeError("Cannot reverse this migration. 'Case.personal_details' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Case.personal_details'
        db.alter_column(u'legalaid_case', 'personal_details_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.PersonalDetails']))

    models = {
        u'legalaid.case': {
            'Meta': {'object_name': 'Case'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'eligibility_check': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['legalaid.EligibilityCheck']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'personal_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.PersonalDetails']", 'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
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
        },
        u'legalaid.deductions': {
            'Meta': {'object_name': 'Deductions'},
            'childcare': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'criminal_legalaid_contributions': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income_tax_and_ni': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'maintenance': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'mortgage_or_rent': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
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
            'on_passported_benefits': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'partner'", 'null': 'True', 'to': u"orm['legalaid.Person']"}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'you': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'you'", 'null': 'True', 'to': u"orm['legalaid.Person']"}),
            'your_problem_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'legalaid.income': {
            'Meta': {'object_name': 'Income'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'earnings': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'other_income': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'self_employed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'legalaid.person': {
            'Meta': {'object_name': 'Person'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'deductions': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Deductions']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Income']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'savings': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Savings']", 'null': 'True', 'blank': 'True'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'mortgage_left': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
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