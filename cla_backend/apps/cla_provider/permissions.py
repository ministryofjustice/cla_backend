from core.permissions import ClientIDPermission


class CLAProviderClientIDPermission(ClientIDPermission):
    client_name = "staff"
    entra_roles = ["Civil Legal Advice - Provider"]
