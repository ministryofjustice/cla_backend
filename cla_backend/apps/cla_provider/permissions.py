from core.permissions import ClientIDPermission


class CLAProviderClientIDPermission(ClientIDPermission):
    client_name = "staff"
    scope = "Client.MCC"
