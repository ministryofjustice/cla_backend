# -*- coding: utf-8 -*-
import os
import re
import sys
from django.core.management.base import BaseCommand

from guidance.models import Note, Tag, NoteTagRelation

meta_regex = re.compile('---\n(.*?)---\n', re.DOTALL)
title_regex = re.compile('title: (.*?)\n')
date_regex = re.compile('date: "(.*?)"\n')
tag_regex = re.compile('  - (.*?)\n')


class Command(BaseCommand):

    help = 'Load Notes in from old markdown files'
    requires_model_validation = True

    def handle(self, *args, **options):

        if len(args) != 1:
            self.stdout.write("Must pass directory for markdown files as arg")
            sys.exit(-1)

        path = args[0]

        for fn in os.listdir(path):
            fp = os.path.join(path, fn)
            if os.path.isfile(fp):
                file_contents = open(fp).read()
                meta_matches = re.findall(meta_regex, file_contents)
                if meta_matches:
                    meta = meta_matches[0]
                    name, ext = os.path.splitext(os.path.basename(fp))
                    title = re.findall(title_regex, meta)[0]
                    date = re.findall(date_regex, meta)[0]
                    tags = re.findall(tag_regex, meta)
                    body = re.sub(meta_regex, '', file_contents).lstrip()

                    note, created = Note.objects.get_or_create(name=name)
                    note.name = name
                    note.title = title
                    note.body = body
                    note.save()
                    self.stdout.write('Saving note: %s - %s' % (name, title))
                    for tag_name in tags:
                        tag, created = Tag.objects.get_or_create(title=tag_name)
                        if tag not in note.tags.all():
                            self.stdout.write('Adding tag %s to %s' % (tag.title, title))
                            note_tag = NoteTagRelation(note=note, tag=tag)
                            note_tag.save()
