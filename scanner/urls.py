from django.urls import path

from .views import delete_all_scans_view, delete_scan_view, export_scans_view, history_view, scan_view

app_name = "scanner"

urlpatterns = [
    path("", scan_view, name="scan"),
    path("history/", history_view, name="history"),
    path("history/delete/<int:scan_id>/", delete_scan_view, name="delete_scan"),
    path("history/delete-all/", delete_all_scans_view, name="delete_all_scans"),
    path("export/", export_scans_view, name="export"),
]
