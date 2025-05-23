from django.contrib.auth import get_user_model
from django.db import models

from src.reviews.models import State
from src.reviews.managers.course_manager import CourseManager, CourseQuerySet


class Course(models.Model):
    faculty    = models.ForeignKey('Faculty', null=True, on_delete=models.SET_NULL, related_name='courses')
    professor  = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='courses')
    name       = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    state = models.CharField(max_length=8, choices=State.choices, default=State.PENDING, db_index=True)
    validated_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    validated_at = models.DateTimeField(null=True, blank=True)

    objects = CourseManager()
    all_objects = CourseQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        unique_together = ('professor', 'name')

    def __str__(self):
        return self.name
