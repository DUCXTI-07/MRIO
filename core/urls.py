from django.urls import path
from .views import (
    ManualUploadView,
    EngineerQueryView,
    SupervisorHistoryView,
    dashboard_view,
    MachineListView,
    ManualListView,
)
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("machines/", MachineListView.as_view(), name="machine-list"),
    path("manuals/", ManualListView.as_view(), name="manual-list"),
    path("upload-manual/", ManualUploadView.as_view(), name="upload-manual"),
    path("query-manual/", EngineerQueryView.as_view(), name="query-manual"),
    path(
        "supervisor/history/",
        SupervisorHistoryView.as_view(),
        name="supervisor-history",
    ),
]
urlpatterns = [
    # Dashboard & API routes...
    path('assistant/', views.dashboard_view, name='dashboard'),
    # Auth Routes
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='core/login.html'),
        name='login',
    ),
    path(
        'logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'
    ),
    path('signup/', views.signup_view, name='signup'),
]