from django.contrib import admin

from .models import Scan


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ("target", "port", "status", "timestamp")
    search_fields = ("target", "status")
    list_filter = ("status",)
