from core.permissions import ClientIDPermission
from cla_auth.constants import PROVIDER_ROLE


class CLAProviderClientIDPermission(ClientIDPermission):
    client_name = "staff"
    entra_roles = [PROVIDER_ROLE]
