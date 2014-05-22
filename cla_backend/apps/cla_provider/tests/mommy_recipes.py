from model_mommy.recipe import Recipe, seq
from ..models import Provider, ProviderAllocation, OutOfHoursRota

provider = Recipe(Provider,
    name=seq('Name'),
)

outofhoursrota = Recipe(OutOfHoursRota)

provider_allocation = Recipe(ProviderAllocation)

