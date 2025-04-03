from django.db import models
from .course import Course


class Exam(models.Model):
    course = models.OneToOneField(Course, related_name="exam", on_delete=models.CASCADE)
    date = models.CharField(max_length=31)
    start = models.PositiveSmallIntegerField()
    end = models.PositiveSmallIntegerField()
