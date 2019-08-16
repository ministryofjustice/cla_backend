class OrganisationMismatchException(Exception):
    pass


class UserIsNotOperatorException(OrganisationMismatchException):
    pass
