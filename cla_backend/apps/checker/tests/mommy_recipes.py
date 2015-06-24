from model_mommy.recipe import Recipe, foreign_key

from ..models import ReasonForContacting, ReasonForContactingCategory

reasonforcontacting = Recipe(ReasonForContacting,
                             _fill_optional=['user_agent', 'referrer'])
reasonforcontacting_category = Recipe(ReasonForContactingCategory,
                                      reason_for_contacting=foreign_key(reasonforcontacting))
