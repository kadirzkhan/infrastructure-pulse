from django.test import TestCase
from django.urls import reverse

from .models import SystemStat


class DashboardTests(TestCase):
    def test_dashboard_renders(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Infrastructure Pulse")

    def test_metrics_api_creates_snapshot(self):
        response = self.client.get(reverse("metrics_api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("cpu", payload)
        self.assertIn("memory", payload)
        self.assertIn("disk", payload)
        self.assertIn("status", payload)
        self.assertEqual(SystemStat.objects.count(), 1)

    def test_history_api_returns_latest_snapshots(self):
        SystemStat.objects.create(
            cpu=42,
            memory=58,
            disk=61,
            memory_used_gb=7.5,
            memory_total_gb=16,
            disk_used_gb=120,
            disk_total_gb=256,
            load_average=1.1,
        )

        response = self.client.get(reverse("history_api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["status"], "healthy")
