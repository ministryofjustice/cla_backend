# coding=utf-8
import datetime
import pytz
from model_mommy.recipe import Recipe, seq

from ..models import Notification


def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def hour_in_past():
    return now() - datetime.timedelta(hours=1)


def hour_in_future():
    return now() + datetime.timedelta(hours=1)


def hours_in_future():
    return now() + datetime.timedelta(hours=2)


notification = Recipe(Notification, notification=seq("Notification"), start_time=hour_in_past, end_time=hour_in_future)


notification_out_of_time = Recipe(
    Notification, notification=seq("Notification"), start_time=hour_in_future, end_time=hours_in_future
)
