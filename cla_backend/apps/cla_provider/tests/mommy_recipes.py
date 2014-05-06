from model_mommy.recipe import Recipe, seq
from ..models import Provider, ProviderAllocation

provider = Recipe(Provider,
    name=seq('Name'),
)

provider_allocation = Recipe(ProviderAllocation)

