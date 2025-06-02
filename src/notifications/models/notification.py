from django.db import models
from django.contrib.auth import get_user_model


class NotificationType(models.TextChoices):
    INFO = "info", "INFO"
    WARNING = "warning", "WARNING"
    ERROR = "error", "ERROR"
    SUCCESS = "success", "SUCCESS"


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=128)
    body = models.TextField()
    type = models.CharField(max_length=16, choices=NotificationType.choices, default=NotificationType.INFO)
    has_been_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
