# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Finance'
        db.delete_table(u'legalaid_finance')

        # Adding model 'Income'
        db.create_table(u'legalaid_income', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('earnings', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('other_income', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('self_employed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'legalaid', ['Income'])

        # Adding model 'Person'
        db.create_table(u'legalaid_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('income', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.Income'], null=True, blank=True)),
            ('savings', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.Savings'], null=True, blank=True)),
            ('deductions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['legalaid.Deductions'], null=True, blank=True)),
        ))
        db.send_create_signal(u'legalaid', ['Person'])

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

        # Adding model 'Deductions'
        db.create_table(u'legalaid_deductions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('income_tax_and_ni', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('maintenance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('mortgage_or_rent', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('criminal_legalaid_contributions', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'legalaid', ['Deductions'])

        # Deleting field 'EligibilityCheck.partner_finances'
        db.delete_column(u'legalaid_eligibilitycheck', 'partner_finances_id')

        # Deleting field 'EligibilityCheck.your_finances'
        db.delete_column(u'legalaid_eligibilitycheck', 'your_finances_id')

        # Adding field 'EligibilityCheck.you'
        db.add_column(u'legalaid_eligibilitycheck', 'you',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='you', null=True, to=orm['legalaid.Person']),
                      keep_default=False)

        # Adding field 'EligibilityCheck.partner'
        db.add_column(u'legalaid_eligibilitycheck', 'partner',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='partner', null=True, to=orm['legalaid.Person']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'Finance'
        db.create_table(u'legalaid_finance', (
            ('income_tax_and_ni', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('investment_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('criminal_legalaid_contributions', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('credit_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('self_employed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('asset_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('mortgage_or_rent', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('earnings', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('maintenance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('bank_balance', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('other_income', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'legalaid', ['Finance'])

        # Deleting model 'Income'
        db.delete_table(u'legalaid_income')

        # Deleting model 'Person'
        db.delete_table(u'legalaid_person')

        # Deleting model 'Savings'
        db.delete_table(u'legalaid_savings')

        # Deleting model 'Deductions'
        db.delete_table(u'legalaid_deductions')

        # Adding field 'EligibilityCheck.partner_finances'
        db.add_column(u'legalaid_eligibilitycheck', 'partner_finances',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='partner_savings', null=True, to=orm['legalaid.Finance'], blank=True),
                      keep_default=False)

        # Adding field 'EligibilityCheck.your_finances'
        db.add_column(u'legalaid_eligibilitycheck', 'your_finances',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='your_savings', null=True, to=orm['legalaid.Finance'], blank=True),
                      keep_default=False)

        # Deleting field 'EligibilityCheck.you'
        db.delete_column(u'legalaid_eligibilitycheck', 'you_id')

        # Deleting field 'EligibilityCheck.partner'
        db.delete_column(u'legalaid_eligibilitycheck', 'partner_id')


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