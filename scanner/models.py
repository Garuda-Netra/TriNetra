from django.db import models


class Scan(models.Model):
    target = models.TextField()
    port = models.IntegerField()
    status = models.TextField()
    timestamp = models.TextField()

    class Meta:
        db_table = "scans"
        managed = False
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.target}:{self.port} {self.status}"
