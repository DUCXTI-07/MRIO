from django.urls import path
from .views import (
    ManualUploadView,
    EngineerQueryView,
    SupervisorHistoryView,
    dashboard_view,
    MachineListView,
    ManualListView,
)

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