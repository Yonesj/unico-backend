from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from src.reviews.fields import RatingField
from .enums import AttendancePolicy, State


class ReviewRevision(models.Model):
    review              = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='revisions')
    state               = models.CharField(max_length=8, choices=State.choices, default=State.PENDING, db_index=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    validated_by        = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    validated_at        = models.DateTimeField(null=True, blank=True)

    grading             = RatingField(blank=True, null=True)
    exam_difficulty     = RatingField(blank=True, null=True)
    general_knowledge   = RatingField(blank=True, null=True)
    homework_difficulty = RatingField(blank=True, null=True)
    teaching_engagement = RatingField(blank=True, null=True)
    exam_resources      = models.CharField(max_length=128 ,blank=True)
    attendance_policy   = models.CharField(max_length=32, choices=AttendancePolicy.choices, blank=True, null=True)
    would_take_again    = models.BooleanField(blank=True, null=True)
    received_score      = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(20.0)]
    )
    review_text          = models.CharField(max_length=350, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Edited review #{self.review.id}"
