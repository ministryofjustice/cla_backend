import datetime
from model_mommy.recipe import Recipe, foreign_key

from ..models import ReasonForContacting, ReasonForContactingCategory, CallbackTimeSlot, ScopeTraversal

reasonforcontacting = Recipe(ReasonForContacting, _fill_optional=["user_agent", "referrer"])
reasonforcontacting_category = Recipe(
    ReasonForContactingCategory, reason_for_contacting=foreign_key(reasonforcontacting)
)
callback_time_slot = Recipe(CallbackTimeSlot, date=datetime.datetime.today().date(), time="0900", capacity=1)
scope_traversal = Recipe(
    ScopeTraversal,
    scope_answers={"question": "Question", "answer": "Answer"},
    category={"name": "Housing, homelessness", "chs_code": "housing"},
    subcategory={"name": "Eviction", "description": "Description"},
    financial_assessment_status="FAST_TRACK",
    fast_track_reason="MORE_INFO_REQUIRED",
)
