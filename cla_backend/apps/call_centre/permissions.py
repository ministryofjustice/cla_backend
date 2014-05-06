from core.permissions import ClientIDPermission


class CallCentreClientIDPermission(ClientIDPermission):
    client_name = 'operator'
