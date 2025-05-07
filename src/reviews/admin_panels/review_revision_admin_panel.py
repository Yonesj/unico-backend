from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction

from src.reviews.models import ReviewRevision, State


@admin.register(ReviewRevision)
class ReviewRevisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'review_link', 'state', 'created_at', 'validated_by', 'validated_at')
    list_filter = ('state', 'created_at')
    search_fields = ('review__review_text','review__user__username','review__course__name')
    ordering = ('-created_at',)
    raw_id_fields = ('review',)
    readonly_fields = ('review','created_at','validated_by','validated_at',)

    fieldsets = (
        (None, {
            'fields': ('review',)
        }),
        ("Original Review", {
            'description': 'The existing approved review; this proposal will overwrite it upon approval.',
            'fields': tuple()
        }),
        ("Proposed Changes", {
            'fields': (
                'grading',
                'exam_difficulty',
                'general_knowledge',
                'homework_difficulty',
                'teaching_engagement',
                'exam_resources',
                'attendance_policy',
                'would_take_again',
                'received_score',
                'review_text'
            )
        }),
        ("Moderation", {
            'fields': ('state', 'validated_by', 'validated_at')
        }),
    )

    def review_link(self, obj):
        """Clickable link to the original review in admin."""
        url = f"/admin/reviews/review/{obj.review_id}/change/"
        return format_html('<a href="{}">Review #{}</a>', url, obj.review_id)

    def save_model(self, request, obj, form, change):
        """
        When the admin flips state to APPROVED, apply only non-null,
        non-empty fields back onto the original Review.
        """
        is_approving = (
                change
                and 'state' in form.changed_data
                and obj.state == State.APPROVED
        )

        with transaction.atomic():
            if change and 'state' in form.changed_data:
                obj.validated_by = request.user
                obj.validated_at = timezone.now()

            super().save_model(request, obj, form, change)

            if is_approving:
                review = obj.review

                for field in [
                    'grading', 'exam_difficulty', 'general_knowledge',
                    'homework_difficulty', 'teaching_engagement',
                    'exam_resources', 'attendance_policy',
                    'would_take_again', 'received_score', 'review_text'
                ]:
                    val = getattr(obj, field)
                    if val is None or (isinstance(val, str) and val == ''):
                        continue
                    setattr(review, field, val)

                review.state = State.APPROVED
                review.validated_by = request.user
                review.validated_at = timezone.now()
                review.save()

    def has_add_permission(self, request):
        return False

    review_link.short_description = "Review"
