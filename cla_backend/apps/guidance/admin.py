# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Note, Tag


class NoteAdmin(admin.ModelAdmin):
    ordering = ['title']

    exclude = ('created', 'modified')
    list_display = ('name', 'title', 'modified', 'created')
    search_fields = ['title']


admin.site.register(Tag)
admin.site.register(Note, NoteAdmin)

