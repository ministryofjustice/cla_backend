# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('organisation', models.CharField(max_length=255, null=True, blank=True)),
                ('service_name', models.CharField(max_length=255, null=True, blank=True)),
                ('service_tag', models.CharField(max_length=50, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('public_description', models.TextField(null=True, blank=True)),
                ('website', models.CharField(max_length=255, null=True, blank=True)),
                ('keywords', models.TextField(null=True, blank=True)),
                ('when_to_use', models.TextField(null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('geographic_coverage', models.CharField(max_length=255, null=True, blank=True)),
                ('type_of_service', models.TextField(null=True, blank=True)),
                ('resource_type', models.CharField(max_length=10, choices=[(b'LEGAL', b'Legal'), (b'OTHER', b'Other')])),
                ('address', models.TextField(null=True, blank=True)),
                ('opening_hours', models.CharField(max_length=255, null=True, blank=True)),
                ('how_to_use', models.TextField(null=True, blank=True)),
                ('accessibility', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name_plural': 'Article categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleCategoryMatrix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('preferred_signpost', models.BooleanField(default=False)),
                ('article', models.ForeignKey(to='knowledgebase.Article')),
                ('article_category', models.ForeignKey(to='knowledgebase.ArticleCategory')),
            ],
            options={
                'verbose_name_plural': 'Article category matrices',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TelephoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('number', models.CharField(max_length=25)),
                ('article', models.ForeignKey(to='knowledgebase.Article')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='article',
            name='article_category',
            field=models.ManyToManyField(to='knowledgebase.ArticleCategory', through='knowledgebase.ArticleCategoryMatrix'),
            preserve_default=True,
        ),
    ]
