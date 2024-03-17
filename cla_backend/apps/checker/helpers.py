from checker.models import CallbackTimeSlot


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
