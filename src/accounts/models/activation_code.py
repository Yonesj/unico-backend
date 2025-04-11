from django.db import models
from .user import User


class ActivationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    code = models.CharField(max_length=8, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
