from model_mommy.recipe import Recipe, seq, foreign_key
from ..models import Provider

provider = Recipe(Provider,
    name=seq('Name'),
)

