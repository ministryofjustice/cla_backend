from model_mommy.recipe import Recipe

from ..models import Operator, Caseworker, Organisation

organisation = Recipe(Organisation)
operator = Recipe(Operator)
caseworker = Recipe(Caseworker)
