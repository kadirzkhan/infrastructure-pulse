from django.db import models


class SystemStat(models.Model):
    cpu = models.FloatField()
    memory = models.FloatField()
    disk = models.FloatField()
    memory_used_gb = models.FloatField(default=0)
    memory_total_gb = models.FloatField(default=0)
    disk_used_gb = models.FloatField(default=0)
    disk_total_gb = models.FloatField(default=0)
    load_average = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"SystemStat(cpu={self.cpu:.1f}, memory={self.memory:.1f}, "
            f"disk={self.disk:.1f}, created_at={self.created_at:%Y-%m-%d %H:%M:%S})"
        )
