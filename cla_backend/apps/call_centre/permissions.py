from core.permissions import ClientIDPermission


class CallCentreClientIDPermission(ClientIDPermission):
    client_id = 'call_centre'
