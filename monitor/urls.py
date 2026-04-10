from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/metrics/", views.metrics_api, name="metrics_api"),
    path("api/history/", views.history_api, name="history_api"),
    path("api/cpu/", views.cpu_api, name="cpu_api"),
    path("api/memory/", views.memory_api, name="memory_api"),
    path("api/disk/", views.disk_api, name="disk_api"),
]
