from model_mommy.recipe import Recipe, seq, foreign_key
from ..models import Provider, ProviderAllocation, OutOfHoursRota, Staff, \
    Feedback


provider = Recipe(Provider,
    name=seq('Name'),
)

staff = Recipe(Staff)

outofhoursrota = Recipe(OutOfHoursRota)

provider_allocation = Recipe(ProviderAllocation)

feedback = Recipe(Feedback, created_by=foreign_key(staff))
