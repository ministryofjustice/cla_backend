class OrganisationMismatchException(Exception):
    pass


class UserIsNotOperatorException(OrganisationMismatchException):
    pass


class OperatorDoesNotBelongToOrganisation(OrganisationMismatchException):
    pass


class CaseNotCreatedByOperatorException(OrganisationMismatchException):
    pass


class CaseCreatorDoesNotBelongToOrganisation(OrganisationMismatchException):
    pass
