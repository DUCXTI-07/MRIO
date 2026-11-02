from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from .views import (
    EngineerQueryView,
    ManualListView,
    ManualUploadView,
    MachineListView,
    SupervisorHistoryView,
    dashboard_view,
    health_check_view,
    signup_view,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("health/", health_check_view, name="health-check"),
    path("api/machines/", MachineListView.as_view(), name="machine-list"),
    path("api/manuals/", ManualListView.as_view(), name="manual-list"),
    path(
        "api/upload-manual/",
        ManualUploadView.as_view(),
        name="upload-manual",
    ),
    path(
        "api/query-manual/",
        EngineerQueryView.as_view(),
        name="query-manual",
    ),
    path(
        "api/supervisor/history/",
        SupervisorHistoryView.as_view(),
        name="supervisor-history",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    path("signup/", signup_view, name="signup"),
    path(
        "assistant/",
        RedirectView.as_view(pattern_name="dashboard", permanent=False),
        name="assistant-dashboard",
    ),
    path(
        "assistant/login/",
        RedirectView.as_view(pattern_name="login", permanent=False),
        name="assistant-login",
    ),
]
