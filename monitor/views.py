from pathlib import Path
import platform
import socket

import psutil
from django.http import JsonResponse
from django.shortcuts import render

from .models import SystemStat

HISTORY_LIMIT = 30
SAMPLE_LIMIT = 120
DISK_ROOT = Path.home().anchor or Path.cwd().anchor or "/"


def dashboard(request):
    context = {
        "host_name": socket.gethostname(),
        "platform_name": platform.system(),
        "platform_release": platform.release(),
        "cpu_count": psutil.cpu_count(),
        "sample_interval_seconds": 3,
    }
    return render(request, "dashboard.html", context)


def _load_average():
    if hasattr(psutil, "getloadavg"):
        try:
            return round(psutil.getloadavg()[0], 2)
        except (OSError, AttributeError):
            return 0
    return 0


def _collect_snapshot():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(DISK_ROOT)
    cpu = round(psutil.cpu_percent(interval=0.2), 2)

    return {
        "cpu": cpu,
        "memory": round(memory.percent, 2),
        "disk": round(disk.percent, 2),
        "memory_used_gb": round(memory.used / (1024 ** 3), 2),
        "memory_total_gb": round(memory.total / (1024 ** 3), 2),
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "load_average": _load_average(),
    }


def _status_from_snapshot(snapshot):
    highest_usage = max(snapshot["cpu"], snapshot["memory"], snapshot["disk"])
    if highest_usage >= 90:
        return "critical"
    if highest_usage >= 75:
        return "warning"
    return "healthy"


def _persist_snapshot(snapshot):
    created = SystemStat.objects.create(**snapshot)

    latest_ids = list(
        SystemStat.objects.order_by("-created_at").values_list("id", flat=True)[:SAMPLE_LIMIT]
    )
    if latest_ids:
        SystemStat.objects.exclude(id__in=latest_ids).delete()

    return created


def metrics_api(request):
    snapshot = _collect_snapshot()
    created = _persist_snapshot(snapshot)

    payload = {
        **snapshot,
        "status": _status_from_snapshot(snapshot),
        "timestamp": created.created_at.isoformat(),
    }
    return JsonResponse(payload)


def cpu_api(request):
    snapshot = _collect_snapshot()
    return JsonResponse({"cpu": snapshot["cpu"]})


def memory_api(request):
    snapshot = _collect_snapshot()
    return JsonResponse(
        {
            "total": snapshot["memory_total_gb"],
            "used": snapshot["memory_used_gb"],
            "percent": snapshot["memory"],
        }
    )


def disk_api(request):
    snapshot = _collect_snapshot()
    return JsonResponse(
        {
            "total": snapshot["disk_total_gb"],
            "used": snapshot["disk_used_gb"],
            "percent": snapshot["disk"],
        }
    )


def history_api(request):
    data = SystemStat.objects.all()[:HISTORY_LIMIT]
    result = [
        {
            "cpu": stat.cpu,
            "memory": stat.memory,
            "disk": stat.disk,
            "memory_used_gb": stat.memory_used_gb,
            "memory_total_gb": stat.memory_total_gb,
            "disk_used_gb": stat.disk_used_gb,
            "disk_total_gb": stat.disk_total_gb,
            "load_average": stat.load_average,
            "status": _status_from_snapshot(
                {"cpu": stat.cpu, "memory": stat.memory, "disk": stat.disk}
            ),
            "time": stat.created_at.strftime("%H:%M:%S"),
        }
        for stat in reversed(data)
    ]
    return JsonResponse(result, safe=False)
