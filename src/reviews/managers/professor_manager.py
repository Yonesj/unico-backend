from django.db import models
from django.db.models import Count, Q, QuerySet
from src.reviews.models import State, Course


class ProfessorQuerySet(models.QuerySet):
    def with_base_eager_loading(self) -> QuerySet:
        return self.select_related('faculty').prefetch_related('courses')

    def with_review_counts(self) -> QuerySet:
        return self.annotate(
            reviews_count=Count(
                'courses__reviews',
                filter=Q(courses__reviews__state=State.APPROVED),
                distinct=True
            )
        )

    def with_view_counts(self) -> QuerySet:
        return self.annotate(
            views_count=Count('page_views')
        )

    def with_stats(self) -> QuerySet:
        return self.with_review_counts().with_view_counts()

    def related_by_courses(self, professor_id):
        course_ids = Course.objects.filter(professor_id=professor_id).values_list('id', flat=True)

        return (
            self
            .annotate(
                shared_courses=Count(
                    'courses',
                    filter=Q(courses__id__in=course_ids),
                    distinct=True
                )
            )
            .filter(shared_courses__gt=0)
            .exclude(pk=professor_id)
            .order_by('-shared_courses')
        )

    def in_same_faculty(self, professor):
        return self.filter(faculty=professor.faculty).exclude(pk=professor.pk).order_by('-overall_rating')


ProfessorManager = models.Manager.from_queryset(ProfessorQuerySet)
