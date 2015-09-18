# -*- coding: utf-8 -*-
from django.contrib import admin

from .admin_support.forms import NoteModelForm
from .models import Note, Tag


class TagInline(admin.TabularInline):
    model = Note.tags.through


class NoteAdmin(admin.ModelAdmin):
    ordering = ['title']

    exclude = ('created', 'modified', 'body')
    list_display = ('name', 'title', 'modified', 'created')
    search_fields = ['title']
    prepopulated_fields = {"name": ("title",)}
    inlines = [TagInline]
    form = NoteModelForm


admin.site.register(Tag)
admin.site.register(Note, NoteAdmin)
