from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


class ActivationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    code = models.CharField(max_length=8, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
