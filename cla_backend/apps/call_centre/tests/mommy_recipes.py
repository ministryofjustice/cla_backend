from model_bakery.recipe import Recipe, foreign_key, seq
from django.contrib.auth.models import User

from ..models import Operator, Caseworker, Organisation

organisation = Recipe(Organisation)
user = Recipe(User, username=seq("user"))
operator = Recipe(Operator, user=foreign_key(user))
caseworker = Recipe(Caseworker, user=foreign_key(user))
