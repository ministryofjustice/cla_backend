# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TelephoneNumber'
        db.create_table(u'knowledgebase_telephonenumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['knowledgebase.Article'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'knowledgebase', ['TelephoneNumber'])

        # Deleting field 'Article.helpline'
        db.delete_column(u'knowledgebase_article', 'helpline')

        # Adding field 'Article.service_tag'
        db.add_column(u'knowledgebase_article', 'service_tag',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Article.email'
        db.add_column(u'knowledgebase_article', 'email',
                      self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'TelephoneNumber'
        db.delete_table(u'knowledgebase_telephonenumber')

        # Adding field 'Article.helpline'
        db.add_column(u'knowledgebase_article', 'helpline',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Article.service_tag'
        db.delete_column(u'knowledgebase_article', 'service_tag')

        # Deleting field 'Article.email'
        db.delete_column(u'knowledgebase_article', 'email')


    models = {
        u'knowledgebase.article': {
            'Meta': {'object_name': 'Article'},
            'accessibility': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'article_category': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['knowledgebase.ArticleCategory']", 'through': u"orm['knowledgebase.ArticleCategoryMatrix']", 'symmetrical': 'False'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'geographic_coverage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'how_to_use': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'opening_hours': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'resource_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'service_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'service_tag': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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
        u'knowledgebase.telephonenumber': {
            'Meta': {'object_name': 'TelephoneNumber'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['knowledgebase.Article']"}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        }
    }

    complete_apps = ['knowledgebase']