import datetime
import logging
from django.conf import settings
from govuk_notify.api import NotifyEmailOrchestrator
from checker.models import CallbackTimeSlot, CALLBACK_TIME_SLOTS

logger = logging.getLogger(__name__)


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
    slots = callback_capacity_get_slots_for_date(date, fallback_to_previous_week=True)
    if not slots:
        # No callback capacity slots were defined for this date so no capacity breach
        return False

    # All slots need to exceed the capacity for it to be a breach
    for slot in slots:
        remaining_capacity = CallbackTimeSlot.get_remaining_capacity_by_dt(slot["capacity"], slot["date"])
        if remaining_capacity > settings.CALLBACK_CAPPING_THRESHOLD:
            return False
    return True


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
            template_id=settings.GOVUK_NOTIFY_TEMPLATES["CALLBACK_CAPACITY_THRESHOLD"],
            personalisation=personalisation,
        )
