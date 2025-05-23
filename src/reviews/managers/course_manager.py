from django.db import models

from src.reviews.models import State


class CourseQuerySet(models.QuerySet):
    def with_base_eager_loading(self):
        return self.select_related('faculty', 'professor')


class CourseManager(models.Manager):
    def get_queryset(self):
        return CourseQuerySet(self.model, using=self._db).filter(state=State.APPROVED)

    def with_base_eager_loading(self):
        return self.get_queryset().with_base_eager_loading()
