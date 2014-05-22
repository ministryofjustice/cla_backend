from model_mommy.recipe import Recipe, seq

from ..models import Provider, ProviderAllocation, Staff

provider = Recipe(Provider,
    name=seq('Name'),
)

staff = Recipe(Staff)

provider_allocation = Recipe(ProviderAllocation)

