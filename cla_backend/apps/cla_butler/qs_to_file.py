# -*- coding: utf-8 -*-
import csv
from datetime import datetime
import json
import logging
import os
import re
import time

from django.db import IntegrityError
from django.db.models import ForeignKey
from django.utils.dateparse import parse_datetime

from jsonfield import JSONField

from cla_common.money_interval.fields import MoneyIntervalField
from cla_common.money_interval.models import MoneyInterval


logger = logging.getLogger(__name__)


RE_DATE = re.compile(r'(\d{4})-(\d{2})-(\d{2})$')
RE_DATETIME = re.compile(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d{6})\+(\d{2}):(\d{2})$')
WRITE_MODE = 'wb'
APPEND_MODE = 'a'


class QuerysetToFile(object):
    def __init__(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self.path = path

    def get_file_path(self, model, ext='csv'):
        return os.path.join(
            self.path,
            '{model}.{extension}'.format(
                model=model.__name__,
                extension=ext))

    def get_name(self, field):
        field_name = field.name
        if isinstance(field, ForeignKey):
            field_name = '{name}_id'.format(name=field_name)
        return field_name

    def get_value(self, instance, field):
        val = getattr(instance, self.get_name(field))
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

    def dump_to_csv(self, qs):
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
            for instance in qs.iterator():
                writer.writerow(
                    [self.get_value(instance, f) for f in
                     qs.model._meta.fields])
            csvfile.close()

    def dump(self, qs):
        logger.info(
            'starting dump of {model}'.format(model=qs.model.__name__))
        start = time.time()
        self.dump_to_csv(qs)
        logger.info(
            'Time to dump {model}: {time}'.format(
                model=qs.model.__name__,
                time=time.time() - start))

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

    def create_object(self, model, row):
        obj = model()
        for f in model._meta.fields:
            n = self.get_name(f)
            try:
                val = self.set_value(row[n], f)
            except Exception as e:
                logger.error(
                    'Failed to convert {value} for {field} to python with '
                    'error: {error}'.format(
                        value=row[n],
                        field=f.name,
                        error=e))
                raise

            try:
                setattr(obj, n, val)
            except Exception as e:
                logger.error(
                    'Failed to set attribute {field}}({class_name}) to '
                    '{value}({value_class}) on object {object} with error: '
                    '{error}'.format(
                        field=f.name,
                        class_name=f.__class__.__name__,
                        value=val,
                        value_class=val.__class__.__name__,
                        object=obj,
                        error=e))
                raise
        return obj

    def populate_and_save(self, model, row):
        obj = self.create_object(model, row)
        saved = False
        try:
            obj.save()
            saved = True
        except IntegrityError:
            logger.info(
                'Try to save failed object: {object} at the end'.format(
                    object=obj))
        except Exception as e:
            logger.error(
                'Failed to save object: {object} with error: {error}'.format(
                    object=obj,
                    error=e))
            raise
        return obj, saved

    def load(self, model):
        """Load .csv file to model"""
        file_path = self.get_file_path(model)

        with open(file_path, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, quoting=csv.QUOTE_ALL)
            failed_objects = []
            for row in reader:
                obj, saved = self.populate_and_save(model, row)

                if not saved:
                    failed_objects.append(obj)

            for failed_obj in failed_objects:
                failed_obj.save()
