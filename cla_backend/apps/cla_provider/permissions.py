from core.permissions import ClientIDPermission
from cla_auth.constants import PROVIDER_ROLE, MCC_OPERATOR


class CLAProviderClientIDPermission(ClientIDPermission):
    client_name = "staff"
    entra_roles = [PROVIDER_ROLE, MCC_OPERATOR]
