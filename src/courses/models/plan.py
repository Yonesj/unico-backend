from uuid import uuid4
from django.db import models
from django.contrib.auth import get_user_model
from .course import Course


User = get_user_model()

class Plan(models.Model):
    share_uuid = models.UUIDField(default=uuid4, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    courses = models.ManyToManyField(Course, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
