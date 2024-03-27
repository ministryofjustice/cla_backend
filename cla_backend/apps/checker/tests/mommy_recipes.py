import datetime
from model_mommy.recipe import Recipe, foreign_key

from ..models import ReasonForContacting, ReasonForContactingCategory, CallbackTimeSlot

reasonforcontacting = Recipe(ReasonForContacting, _fill_optional=["user_agent", "referrer"])
reasonforcontacting_category = Recipe(
    ReasonForContactingCategory, reason_for_contacting=foreign_key(reasonforcontacting)
)
callback_time_slot = Recipe(CallbackTimeSlot, date=datetime.datetime.today().date(), time="0900", capacity=1)
