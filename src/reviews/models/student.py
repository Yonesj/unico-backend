from django.db import models
from django.contrib.auth import get_user_model


class Student(models.Model):
    student_id = models.BigIntegerField(primary_key=True, unique=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    faculty = models.CharField(max_length=64)
    major = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
