from rest_framework.permissions import BasePermission

class HasRolePermission(BasePermission):
    """
    Permission check based on the role in the Profile model.

    This permission class checks if the user is authenticated and if the user's profile role is in the list of required roles.
    """

    def has_permission(self, request, view):
        """
        Determine if the user has permission to access the view.

        The user has permission if they are authenticated and their profile role is in the list of required roles.
        """
        # Get the required roles from the view
        required_roles = getattr(view, 'required_roles', [])

        # If the view does not specify any required roles, allow access
        if not required_roles:
            return True

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user's profile role is in the list of required roles
        return request.user.profile.role in required_roles