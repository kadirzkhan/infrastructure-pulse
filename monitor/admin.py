from django.contrib import admin
from .models import SystemStat


@admin.register(SystemStat)
class SystemStatAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "cpu",
        "memory",
        "disk",
        "memory_used_gb",
        "disk_used_gb",
        "load_average",
    )
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    search_fields = ("created_at",)
