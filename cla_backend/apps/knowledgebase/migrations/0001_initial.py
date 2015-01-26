# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from core.south_utils import FakeFirstMigration


class Migration(FakeFirstMigration, SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table(u'knowledgebase_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('service_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('when_to_use', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('helpline', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('geographic_coverage', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('type_of_service', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('resource_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('opening_hours', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('how_to_use', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('accessibility', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'knowledgebase', ['Article'])

        # Adding model 'ArticleCategory'
        db.create_table(u'knowledgebase_articlecategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'knowledgebase', ['ArticleCategory'])

        # Adding model 'ArticleCategoryMatrix'
        db.create_table(u'knowledgebase_articlecategorymatrix', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['knowledgebase.Article'])),
            ('article_category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['knowledgebase.ArticleCategory'])),
            ('preferred_signpost', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'knowledgebase', ['ArticleCategoryMatrix'])


    def backwards(self, orm):
        # Deleting model 'Article'
        db.delete_table(u'knowledgebase_article')

        # Deleting model 'ArticleCategory'
        db.delete_table(u'knowledgebase_articlecategory')

        # Deleting model 'ArticleCategoryMatrix'
        db.delete_table(u'knowledgebase_articlecategorymatrix')


    models = {
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
        }
    }

    complete_apps = ['knowledgebase']