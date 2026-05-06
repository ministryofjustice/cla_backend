from cla_backend.apps.cla_provider.forms import SplitBaseCaseForm


class SplitMCCCaseForm(SplitBaseCaseForm):
    # Doesn't care about an `already split` case or if case is being split by `same-category`
    pass
