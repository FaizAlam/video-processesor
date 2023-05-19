from django.db import models

class TemporaryFile(models.Model):
    file = models.FileField()

    # Optional fields
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
