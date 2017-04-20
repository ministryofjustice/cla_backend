# -*- coding: utf-8 -*-
import csv
from datetime import datetime
import json
import os
import re

from django.core.exceptions import ValidationError
from django.db.models import ForeignKey
from django.utils.dateparse import parse_datetime
from jsonfield import JSONField

from cla_common.money_interval.fields import MoneyIntervalField
from cla_common.money_interval.models import MoneyInterval

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')
RE_DATETIME = re.compile(r'(\d{4})-(\d\d?)-(\d\d?) (\d\d?):(\d\d?):(\d\d?)\.(\d{6})\+(\d\d?):(\d\d?)$')
WRITE_MODE = 'wb'
APPEND_MODE = 'a'


class QuerysetToCsv(object):
    def __init__(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self.path = path

    def get_file_path(self, model):
        return os.path.join(self.path, '%s.csv' % model.__name__)

    def get_name(self, field):
        field_name = field.name
        if isinstance(field, ForeignKey):
            field_name = '%s_id' % field_name
        return field_name

    def get_value(self, row, field):
        val = row[self.get_name(field)]
        if isinstance(val, MoneyInterval):
            val = json.dumps(val.as_dict())
        if hasattr(val, 'pk'):
            val = val.pk
        if val is None:
            val = ''
        try:
            return unicode(val).encode('utf-8')
        except UnicodeDecodeError:
            return val

    def dump(self, qs):
        """dump queryset to .csv"""
        file_path = self.get_file_path(qs.model)

        if os.path.isfile(file_path):
            write_mode = APPEND_MODE
        else:
            write_mode = WRITE_MODE

        field_names = [self.get_name(f) for f in qs.model._meta.fields]
        with open(file_path, write_mode) as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            if write_mode == WRITE_MODE:
                writer.writerow(field_names)
            for row in qs.values():
                writer.writerow(
                    [self.get_value(row, f) for f in
                     qs.model._meta.fields])
            csvfile.close()

    def set_value(self, val, field):
        if val == '' and field.empty_strings_allowed and not field.null:
            val = ''
        elif val in field.empty_values:
            val = None
        elif isinstance(field, MoneyIntervalField):
            val = MoneyInterval.from_dict(json.loads(val))
        elif isinstance(field, JSONField):
            val = json.dumps(val)
        elif RE_DATE.match(val):
            val = datetime.strptime(val, '%Y-%m-%d').date()
        elif RE_DATETIME.match(val):
            val = parse_datetime(val)
        return val

    def load(self, model):
        """Load .csv file to model"""
        file_path = self.get_file_path(model)

        with open(file_path, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, quoting=csv.QUOTE_ALL)
            for row in reader:
                obj = model()
                for f in model._meta.fields:
                    n = self.get_name(f)
                    val = self.set_value(row[n], f)
                    try:
                        setattr(obj, n, val)
                    except Exception as set_e:
                        print set_e
                        print val
                        print val.__class__.__name__
                        print f.name
                        print f.__class__.__name__
                        raise

                try:
                    obj.save()
                except Exception as e:
                    print e
                    raise
