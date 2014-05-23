from model_mommy.recipe import Recipe, seq
from ..models import Provider, ProviderAllocation, OutOfHoursRota, Staff


provider = Recipe(Provider,
    name=seq('Name'),
)

staff = Recipe(Staff)

outofhoursrota = Recipe(OutOfHoursRota)

provider_allocation = Recipe(ProviderAllocation)

