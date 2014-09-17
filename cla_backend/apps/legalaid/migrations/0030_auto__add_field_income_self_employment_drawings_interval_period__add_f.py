# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Income.self_employment_drawings_interval_period'
        db.add_column(u'legalaid_income', 'self_employment_drawings_interval_period',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.self_employment_drawings_per_interval_value'
        db.add_column(u'legalaid_income', 'self_employment_drawings_per_interval_value',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.self_employment_drawings'
        db.add_column(u'legalaid_income', 'self_employment_drawings',
                      self.gf('cla_common.money_interval.fields.MoneyIntervalField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.benefits_interval_period'
        db.add_column(u'legalaid_income', 'benefits_interval_period',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.benefits_per_interval_value'
        db.add_column(u'legalaid_income', 'benefits_per_interval_value',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.benefits'
        db.add_column(u'legalaid_income', 'benefits',
                      self.gf('cla_common.money_interval.fields.MoneyIntervalField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.tax_credits_interval_period'
        db.add_column(u'legalaid_income', 'tax_credits_interval_period',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.tax_credits_per_interval_value'
        db.add_column(u'legalaid_income', 'tax_credits_per_interval_value',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.tax_credits'
        db.add_column(u'legalaid_income', 'tax_credits',
                      self.gf('cla_common.money_interval.fields.MoneyIntervalField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.child_benefits_interval_period'
        db.add_column(u'legalaid_income', 'child_benefits_interval_period',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.child_benefits_per_interval_value'
        db.add_column(u'legalaid_income', 'child_benefits_per_interval_value',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.child_benefits'
        db.add_column(u'legalaid_income', 'child_benefits',
                      self.gf('cla_common.money_interval.fields.MoneyIntervalField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.maintenance_received_interval_period'
        db.add_column(u'legalaid_income', 'maintenance_received_interval_period',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.maintenance_received_per_interval_value'
        db.add_column(u'legalaid_income', 'maintenance_received_per_interval_value',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.maintenance_received'
        db.add_column(u'legalaid_income', 'maintenance_received',
                      self.gf('cla_common.money_interval.fields.MoneyIntervalField')(default=None, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.pension_interval_period'
        db.add_column(u'legalaid_income', 'pension_interval_period',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.pension_per_interval_value'
        db.add_column(u'legalaid_income', 'pension_per_interval_value',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Income.pension'
        db.add_column(u'legalaid_income', 'pension',
                      self.gf('cla_common.money_interval.fields.MoneyIntervalField')(default=None, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Income.self_employment_drawings_interval_period'
        db.delete_column(u'legalaid_income', 'self_employment_drawings_interval_period')

        # Deleting field 'Income.self_employment_drawings_per_interval_value'
        db.delete_column(u'legalaid_income', 'self_employment_drawings_per_interval_value')

        # Deleting field 'Income.self_employment_drawings'
        db.delete_column(u'legalaid_income', 'self_employment_drawings')

        # Deleting field 'Income.benefits_interval_period'
        db.delete_column(u'legalaid_income', 'benefits_interval_period')

        # Deleting field 'Income.benefits_per_interval_value'
        db.delete_column(u'legalaid_income', 'benefits_per_interval_value')

        # Deleting field 'Income.benefits'
        db.delete_column(u'legalaid_income', 'benefits')

        # Deleting field 'Income.tax_credits_interval_period'
        db.delete_column(u'legalaid_income', 'tax_credits_interval_period')

        # Deleting field 'Income.tax_credits_per_interval_value'
        db.delete_column(u'legalaid_income', 'tax_credits_per_interval_value')

        # Deleting field 'Income.tax_credits'
        db.delete_column(u'legalaid_income', 'tax_credits')

        # Deleting field 'Income.child_benefits_interval_period'
        db.delete_column(u'legalaid_income', 'child_benefits_interval_period')

        # Deleting field 'Income.child_benefits_per_interval_value'
        db.delete_column(u'legalaid_income', 'child_benefits_per_interval_value')

        # Deleting field 'Income.child_benefits'
        db.delete_column(u'legalaid_income', 'child_benefits')

        # Deleting field 'Income.maintenance_received_interval_period'
        db.delete_column(u'legalaid_income', 'maintenance_received_interval_period')

        # Deleting field 'Income.maintenance_received_per_interval_value'
        db.delete_column(u'legalaid_income', 'maintenance_received_per_interval_value')

        # Deleting field 'Income.maintenance_received'
        db.delete_column(u'legalaid_income', 'maintenance_received')

        # Deleting field 'Income.pension_interval_period'
        db.delete_column(u'legalaid_income', 'pension_interval_period')

        # Deleting field 'Income.pension_per_interval_value'
        db.delete_column(u'legalaid_income', 'pension_per_interval_value')

        # Deleting field 'Income.pension'
        db.delete_column(u'legalaid_income', 'pension')


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
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
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
        u'diagnosis.diagnosistraversal': {
            'Meta': {'object_name': 'DiagnosisTraversal'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'current_node_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'nodes': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'UNKNOWN'", 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'knowledgebase.article': {
            'Meta': {'object_name': 'Article'},
            'accessibility': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'article_category': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['knowledgebase.ArticleCategory']", 'through': u"orm['knowledgebase.ArticleCategoryMatrix']", 'symmetrical': 'False'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geographic_coverage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'helpline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'how_to_use': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'opening_hours': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type_of_service': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'when_to_use': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'knowledgebase.articlecategory': {
            'Meta': {'object_name': 'ArticleCategory'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'knowledgebase.articlecategorymatrix': {
            'Meta': {'object_name': 'ArticleCategoryMatrix'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['knowledgebase.Article']"}),
            'article_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['knowledgebase.ArticleCategory']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'preferred_signpost': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'legalaid.adaptationdetails': {
            'Meta': {'object_name': 'AdaptationDetails'},
            'bsl_webcam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'callback_preference': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
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
            'alternative_help_articles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['knowledgebase.Article']", 'null': 'True', 'through': u"orm['legalaid.CaseKnowledgebaseAssignment']", 'blank': 'True'}),
            'billable_time': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'diagnosis': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['diagnosis.DiagnosisTraversal']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'ecf_statement': ('django.db.models.fields.CharField', [], {'max_length': '35', 'null': 'True', 'blank': 'True'}),
            'eligibility_check': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['legalaid.EligibilityCheck']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'exempt_user': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'exempt_user_reason': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'from_case': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'split_cases'", 'null': 'True', 'to': u"orm['legalaid.Case']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laa_reference': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'locked_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'locked_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'case_locked'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'matter_type1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['legalaid.MatterType']"}),
            'matter_type2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['legalaid.MatterType']"}),
            'media_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.MediaCode']", 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'outcome_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'outcome_code_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'personal_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.PersonalDetails']", 'null': 'True', 'blank': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cla_provider.Provider']", 'null': 'True', 'blank': 'True'}),
            'provider_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'requires_action_by': ('django.db.models.fields.CharField', [], {'default': "'operator'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'thirdparty_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.ThirdPartyDetails']", 'null': 'True', 'blank': 'True'})
        },
        u'legalaid.caseknowledgebaseassignment': {
            'Meta': {'object_name': 'CaseKnowledgebaseAssignment'},
            'alternative_help_article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['knowledgebase.Article']"}),
            'assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Case']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        u'legalaid.category': {
            'Meta': {'ordering': "['order']", 'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ecf_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'raw_description': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'legalaid.deductions': {
            'Meta': {'object_name': 'Deductions'},
            'childcare': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'childcare_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'childcare_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'criminal_legalaid_contributions': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income_tax': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'income_tax_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'income_tax_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'maintenance': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'maintenance_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'maintenance_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'mortgage': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'mortgage_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'mortgage_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'national_insurance': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'national_insurance_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'national_insurance_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rent': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'rent_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rent_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'legalaid.eligibilitycheck': {
            'Meta': {'object_name': 'EligibilityCheck'},
            'calculations': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Category']", 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'dependants_old': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'dependants_young': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'disputed_savings': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Savings']", 'null': 'True', 'blank': 'True'}),
            'has_partner': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_you_or_your_partner_over_60': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'on_nass_benefits': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'on_passported_benefits': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'partner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'partner'", 'null': 'True', 'to': u"orm['legalaid.Person']"}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '50'}),
            'you': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'you'", 'null': 'True', 'to': u"orm['legalaid.Person']"}),
            'your_problem_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'legalaid.income': {
            'Meta': {'object_name': 'Income'},
            'benefits': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'benefits_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'benefits_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'child_benefits': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'child_benefits_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'child_benefits_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'earnings': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'earnings_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'earnings_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintenance_received': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'maintenance_received_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'maintenance_received_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'other_income': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'other_income_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'other_income_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pension': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'pension_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'pension_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'self_employed': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'self_employment_drawings': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'self_employment_drawings_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'self_employment_drawings_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tax_credits': ('cla_common.money_interval.fields.MoneyIntervalField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'tax_credits_interval_period': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tax_credits_per_interval_value': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'legalaid.mattertype': {
            'Meta': {'unique_together': "(('code', 'level'),)", 'object_name': 'MatterType'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.Category']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        u'legalaid.mediacode': {
            'Meta': {'object_name': 'MediaCode'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.MediaCodeGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'legalaid.mediacodegroup': {
            'Meta': {'object_name': 'MediaCodeGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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
            'case_count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'contact_for_research': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'ni_number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'safe_to_contact': ('django.db.models.fields.CharField', [], {'default': "'SAFE'", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'vulnerable_user': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'legalaid.property': {
            'Meta': {'object_name': 'Property'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'disputed': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'eligibility_check': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.EligibilityCheck']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'mortgage_left': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'}),
            'share': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'value': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'})
        },
        u'legalaid.savings': {
            'Meta': {'object_name': 'Savings'},
            'asset_balance': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'}),
            'bank_balance': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'credit_balance': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investment_balance': ('legalaid.fields.MoneyField', [], {'default': 'None', 'max_value': '9999999999', 'min_value': '0', 'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        },
        u'legalaid.thirdpartydetails': {
            'Meta': {'object_name': 'ThirdPartyDetails'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'no_contact_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'organisation_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pass_phrase': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'personal_details': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['legalaid.PersonalDetails']"}),
            'personal_relationship': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'personal_relationship_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'reference': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'spoke_to': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['legalaid']