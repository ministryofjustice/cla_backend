# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ThirdPartyDetails.personal_relationship_note'
        db.add_column(u'legalaid_thirdpartydetails', 'personal_relationship_note',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ThirdPartyDetails.personal_relationship_note'
        db.delete_column(u'legalaid_thirdpartydetails', 'personal_relationship_note')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cla_provider.provider': {
            'Meta': {'object_name': 'Provider'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'law_category': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['legalaid.Category']", 'through': u"orm['cla_provider.ProviderAllocation']", 'symmetrical': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'opening_hours': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telephone_backdoor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telephone_frontdoor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'cla_provider.providerallocation': {
            'Meta': {'object_name': 'ProviderAllocation'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Category']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cla_provider.Provider']"}),
            'weighted_distribution': ('django.db.models.fields.FloatField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'legalaid.adaptationdetails': {
            'Meta': {'object_name': 'AdaptationDetails'},
            'bsl_webcam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'minicom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'skype_webcam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text_relay': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'legalaid.case': {
            'Meta': {'object_name': 'Case'},
            'adaptation_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.AdaptationDetails']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'eligibility_check': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['legalaid.EligibilityCheck']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_scope': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'laa_reference': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'locked_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'locked_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'case_locked'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'personal_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.PersonalDetails']", 'null': 'True', 'blank': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cla_provider.Provider']", 'null': 'True', 'blank': 'True'}),
            'provider_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '50'}),
            'thirdparty_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.ThirdPartyDetails']", 'null': 'True', 'blank': 'True'})
        },
        u'legalaid.caselog': {
            'Meta': {'ordering': "['-created']", 'object_name': 'CaseLog'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Case']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.CaseLogType']"}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'legalaid.caselogtype': {
            'Meta': {'ordering': "['code']", 'object_name': 'CaseLogType'},
            'action_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'childcare': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'childcare_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'childcare_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'criminal_legalaid_contributions': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income_tax': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'income_tax_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'income_tax_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'maintenance': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'maintenance_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'maintenance_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'mortgage': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'mortgage_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'mortgage_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'national_insurance': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'national_insurance_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'national_insurance_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rent': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'rent_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rent_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'on_nass_benefits': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'on_passported_benefits': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'partner'", 'null': 'True', 'to': u"orm['legalaid.Person']"}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'maybe'", 'max_length': '50'}),
            'you': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'you'", 'null': 'True', 'to': u"orm['legalaid.Person']"}),
            'your_problem_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'legalaid.income': {
            'Meta': {'object_name': 'Income'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'earnings': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'earnings_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'earnings_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'other_income': ('cla_common.money_interval.fields.MoneyIntervalField', [], {}),
            'other_income_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'other_income_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
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
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'legalaid.property': {
            'Meta': {'object_name': 'Property'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'disputed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eligibility_check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.EligibilityCheck']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'mortgage_left': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'}),
            'share': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'value': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'})
        },
        u'legalaid.savings': {
            'Meta': {'object_name': 'Savings'},
            'asset_balance': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'}),
            'bank_balance': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'credit_balance': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_balance': ('legalaid.fields.MoneyField', [], {'default': '0', 'max_value': '9999999999', 'min_value': '0'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        u'legalaid.thirdpartydetails': {
            'Meta': {'object_name': 'ThirdPartyDetails'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'pass_phrase': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'personal_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.PersonalDetails']"}),
            'personal_relationship': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'personal_relationship_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        }
    }

    complete_apps = ['legalaid']