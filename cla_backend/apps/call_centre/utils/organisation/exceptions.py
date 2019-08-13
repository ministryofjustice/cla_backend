class OrganisationMatchException(Exception):
    pass


class UserIsNotOperatorException(OrganisationMatchException):
    pass


class OperatorDoesNotBelongToOrganisation(OrganisationMatchException):
    pass


class CaseNotCreatedByOperatorException(OrganisationMatchException):
    pass


class CaseCreatorDoesNotBelongToOrganisation(OrganisationMatchException):
    pass
