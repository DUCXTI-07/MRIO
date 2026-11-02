from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
  """Allows access only to users belonging to the Administrator role/staff."""

  def has_permission(self, request, view):
    return request.user and request.user.is_authenticated and (
        request.user.is_staff or request.user.groups.filter(
            name='Administrator'
        ).exists()
    )


class IsEngineer(BasePermission):
  """Allows access for authenticated engineers."""

  def has_permission(self, request, view):
    return request.user and request.user.is_authenticated


class IsSupervisor(BasePermission):
  """Allows read-only access for supervisors to audit logs."""

  def has_permission(self, request, view):
    return request.user and request.user.is_authenticated and (
        request.user.is_staff or request.user.groups.filter(
            name='Supervisor'
        ).exists()
    )