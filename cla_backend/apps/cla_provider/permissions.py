from core.permissions import ClientIDPermission


class CLAProviderClientIDPermission(ClientIDPermission):
    client_id = 'cla_provider'
