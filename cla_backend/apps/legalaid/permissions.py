from rest_framework.permissions import BasePermission


class IsManagerOrMePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        usermodel_instance = view.get_logged_in_user_model()
        # this doesn't check if usermodel_instance.provider == obj.provider
        # that is handled by get_queryset()
        return usermodel_instance == obj or usermodel_instance.is_manager
