class InvalidMutationException(Exception):
    """
    Raised when an action is not permitted because it would generate an
    inconsistent state.
    E.g. closing a case when it shouldn't be closed.
    """
    pass
