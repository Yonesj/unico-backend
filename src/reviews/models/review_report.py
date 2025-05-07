from django.db import models
from django.contrib.auth import get_user_model


class ReviewReportChoices(models.TextChoices):
    POLICY_VIOLATION = 'policy_violation', 'Policy violation'
    SPAM             = 'spam',             'Spam or advertising'
    OTHER            = 'other',            'Other'


class ReviewReport(models.Model):
    reporter     = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    review       = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='reports')
    reported_at  = models.DateTimeField(auto_now_add=True)
    reason       = models.CharField(max_length=16, choices=ReviewReportChoices.choices, default=ReviewReportChoices.POLICY_VIOLATION)

    class Meta:
        unique_together = ('reporter', 'review')

    def __str__(self):
        return f'{self.reporter} reported review #{self.review.id} ({self.get_reason_display()})'
