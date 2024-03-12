import csv
import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from checker.models import CallbackTimeSlot, CALLBACK_TIME_SLOTS

CSV_COL_DATE = 0
CSV_COL_TIME = 1
CSV_COL_CAPACITY = 2


class CallbackTimeSlotCSVImporter(object):
    @classmethod
    def parse(cls, csv_file_handler):
        rows = []
        errors = []
        reader = csv.reader(csv_file_handler, delimiter=",")
        for index, row in enumerate(reader):
            try:
                cls.validate_row(row)
                rows.append(cls.get_callback_time_slot_from_row(row))
            except ValidationError as e:
                for _, message in e.message_dict.items():
                    errors.append("Row %s: %s" % (index + 1, message))
            except Exception as e:
                errors.append("Row %s: %s" % (index + 1, str(e)))
        return [rows, errors]

    @classmethod
    def save(cls, rows):
        with transaction.atomic():
            for row in rows:
                row.save()

    @classmethod
    def validate_row(cls, row):
        try:
            row[CSV_COL_DATE] = datetime.datetime.strptime(row[CSV_COL_DATE], "%d/%m/%Y")
        except Exception as error:
            raise ValidationError(
                message=dict(date="Write the date in this format: dd/mm/yyyy")
            )
        if row[CSV_COL_TIME] not in CALLBACK_TIME_SLOTS:
            raise ValidationError(message=dict(time="Check the time is correct, for example, 1500 (for the 1500 to 1530 slot)"))
        try:
            assert int(row[CSV_COL_CAPACITY]) >= 0
        except ValueError as error:
            raise ValidationError(message=dict(capacity="Write capacity as a number, for example: 1, 2, 10"))
        except AssertionError as error:
            raise ValidationError(message=dict(capacity="The capacity must be 0 or more"))
        except Exception as error:
            raise ValidationError(message=dict(capacity=error))

    @classmethod
    def get_callback_time_slot_from_row(self, row):
        data = dict(date=row[CSV_COL_DATE], time=row[CSV_COL_TIME])
        try:
            model = CallbackTimeSlot.objects.get(**data)
        except CallbackTimeSlot.DoesNotExist:
            model = CallbackTimeSlot(**data)
        except Exception as error:
            raise ValidationError(error)

        model.capacity = row[CSV_COL_CAPACITY]
        return model
