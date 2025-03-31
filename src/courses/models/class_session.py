from django.db import models
from .course import Course, WeekDay


class ClassSession(models.Model):
    course = models.ForeignKey(Course, related_name="classes", on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=WeekDay, default=WeekDay.NONE)
    start = models.PositiveSmallIntegerField()
    end = models.PositiveSmallIntegerField()
    is_problem_solving = models.BooleanField(default=False)
