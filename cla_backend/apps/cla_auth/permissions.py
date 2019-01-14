from django.conf import settings
from rest_framework import permissions


class OBIEEIPPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        ip_addr = request.META["REMOTE_ADDR"]
        whitelist = settings.OBIEE_IP_PERMISSIONS

        return "*" in whitelist or ip_addr in whitelist
