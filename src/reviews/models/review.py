from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from src.reviews.fields import RatingField
from src.reviews.managers import ReviewManager, ReviewQuerySet
from .enums import State, AttendancePolicy


class Review(models.Model):
    user                 = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, related_name='reviews')
    course               = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='reviews')
    created_at           = models.DateTimeField(auto_now_add=True)

    state                = models.CharField(max_length=8, choices=State.choices, default=State.PENDING, db_index=True)
    validated_by         = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    validated_at         = models.DateTimeField(null=True, blank=True)

    grading              = RatingField()
    exam_difficulty      = RatingField()
    general_knowledge    = RatingField()
    homework_difficulty  = RatingField()
    teaching_engagement  = RatingField()

    exam_resources       = models.CharField(max_length=128, blank=True)
    attendance_policy    = models.CharField(max_length=32, choices=AttendancePolicy.choices)
    would_take_again     = models.BooleanField(blank=False)
    received_score       = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(20.0)]
    )

    review_text          = models.CharField(max_length=350, blank=True)

    objects = ReviewManager()
    all_objects = ReviewQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        unique_together = [('user', 'course')]

    def __str__(self):
        return f"Review by {self.user} for {self.course}"
