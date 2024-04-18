import csv
import datetime
import codecs
from django.db import transaction
from django.core.exceptions import ValidationError
from checker.models import CallbackTimeSlot, CALLBACK_TIME_SLOTS
import logging
from django.conf import settings
from govuk_notify.api import NotifyEmailOrchestrator

logger = logging.getLogger(__name__)

CSV_COL_DATE = 0
CSV_COL_TIME = 1
CSV_COL_CAPACITY = 2


class CallbackTimeSlotCSVImporter(object):
    @classmethod
    def parse(cls, csv_file_handler):
        rows = []
        errors = []
        reader = csv.reader(codecs.iterdecode(csv_file_handler, "utf-8-sig"), delimiter=",")
        for index, row in enumerate(reader):
            try:
                cls.validate_row(row)
                rows.append(cls.get_callback_time_slot_from_row(row))
            except ValidationError as e:
                for _, message in e:
                    errors.append("Row %s: %s" % (index + 1, message[0]))
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
        """Validates a row in the callback CSV, transforming the data types to those appropriate for the CallbackTimeslot Model.

        Args:
            row (List): List of strings in the format [dd/mm/yyyy, HHMM, int]

        Raises:
            ValidationError: When the data is unable to be transformed into those required for a valid callback this exception will be raised.
        """
        try:
            row[CSV_COL_DATE] = datetime.datetime.strptime(row[CSV_COL_DATE], "%d/%m/%Y").date()
        except Exception:
            raise ValidationError(message=dict(date="Write the date in this format: dd/mm/yyyy"))
        try:
            time = row[CSV_COL_TIME].strip()
            # Excel will sometimes remove the leading zero from values it interprets as numbers.
            if time in ["900", "930"]:
                time = "0{time}".format(time=time)
            assert time in CALLBACK_TIME_SLOTS
            row[CSV_COL_TIME] = time
        except Exception:
            raise ValidationError(
                message=dict(time="Check the time is correct, for example, 1500 (for the 1500 to 1530 slot)")
            )

        try:
            assert int(row[CSV_COL_CAPACITY]) >= 0
            row[CSV_COL_CAPACITY] = int(row[CSV_COL_CAPACITY])
        except ValueError:
            raise ValidationError(message=dict(capacity="Write capacity as a number, for example: 1, 2, 10"))
        except AssertionError:
            raise ValidationError(message=dict(capacity="The capacity must be 0 or more"))
        except Exception:
            raise ValidationError(message=dict(capacity="Write capacity as a number, for example: 1, 2, 10"))

    @classmethod
    def get_callback_time_slot_from_row(cls, row):
        data = dict(date=row[CSV_COL_DATE], time=row[CSV_COL_TIME])
        try:
            model = CallbackTimeSlot.objects.get(**data)
        except CallbackTimeSlot.DoesNotExist:
            model = CallbackTimeSlot(**data)
        except Exception as error:
            raise ValidationError(error)

        model.capacity = row[CSV_COL_CAPACITY]
        return model


def get_timeslot_of_datetime(slot_start_datetime):
    """Gets the timeslot of a given datetime.

    Args:
        slot_start_datetime (datetime): datetime of the slot starting time.

    Returns:
        models.CallbackTimeSlot | None: Timeslot or None, if none are found
    """
    slot_start_time = slot_start_datetime.strftime("%H%M")
    timeslots = CallbackTimeSlot.objects.filter(date=slot_start_datetime.date(), time=slot_start_time).all()
    return None if len(timeslots) == 0 else timeslots[0]


def callback_capacity_get_slots_for_date(date, fallback_to_previous_week=True):
    slots = []
    for slot, _ in CALLBACK_TIME_SLOTS.CHOICES:
        dt = datetime.datetime.combine(date, CallbackTimeSlot.get_time_from_interval_string(slot)).replace(
            tzinfo=date.tzinfo
        )
        _, slot = CallbackTimeSlot.get_model_from_datetime(dt, fallback_to_previous_week)
        if slot:
            slots.append({"date": dt, "capacity": slot.capacity})
    return slots


def callback_capacity_threshold_breached(date):
    # All slots need to exceed the capacity for it to be a breach
    return CallbackTimeSlot.is_threshold_breached_on_date(date)


def callback_capacity_threshold_breach_send_notification(dt):
    dt_str = dt.strftime("%d %B %Y")
    logger.info("Sending email for capacity threshold breach for date {}".format(dt_str))
    if not settings.CALLBACK_CAPPING_THRESHOLD_NOTIFICATION:
        logger.info("Could not send email due to missing CALLBACK_CAPPING_THRESHOLD_NOTIFICATION setting")
        return

    personalisation = {"date": dt_str}
    email = NotifyEmailOrchestrator()
    email_addresses = settings.CALLBACK_CAPPING_THRESHOLD_NOTIFICATION.split(",")
    for email_address in email_addresses:
        email.send_email(
            email_address=email_address,
            template_id=settings.GOVUK_NOTIFY_TEMPLATES["CALLBACK_NO_CAPACITY_ALERT"],
            personalisation=personalisation,
        )
