from django.db import models
from django.db.models import Count, Q, QuerySet

from src.reviews.models import ReviewReactionChoices, State


class ReviewQuerySet(models.QuerySet):
    def with_base_eager_loading(self) -> QuerySet:
        return self.select_related('course').select_related('course__professor').prefetch_related('reactions')

    def with_likes(self) -> QuerySet:
        return self.annotate(
            likes_count=Count(
                'reactions',
                filter=Q(reactions__value=ReviewReactionChoices.LIKE),
            )
        )

    def with_dislikes(self) -> QuerySet:
        return self.annotate(
            dislikes_count=Count(
                'reactions',
                filter=Q(reactions__value=ReviewReactionChoices.DISLIKE),
            )
        )

    def with_stats(self) -> QuerySet:
        return self.with_likes().with_dislikes()


class ReviewManager(models.Manager):
    def get_queryset(self):
        return ReviewQuerySet(self.model, using=self._db).filter(state=State.APPROVED)

    def with_base_eager_loading(self):
        return self.get_queryset().with_base_eager_loading()

    def with_likes(self):
        return self.get_queryset().with_likes()

    def with_dislikes(self):
        return self.get_queryset().with_dislikes()

    def with_stats(self):
        return self.get_queryset().with_stats()
