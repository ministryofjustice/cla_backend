from model_mommy.recipe import Recipe, seq
from ..models import Provider

provider = Recipe(Provider,
    name=seq('Name'),
)

