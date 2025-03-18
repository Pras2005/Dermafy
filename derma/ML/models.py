from django.db import models
from django.conf import settings


class SkincareRoutine(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    routine = models.JSONField()
    recommended_products = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Routine for {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
