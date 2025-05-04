from django.db import models

from src.reviews.fields import RatingAvgField
from src.utill.validators import FileSizeValidator


class Professor(models.Model):
    faculty                  = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True, related_name='professors')

    first_name               = models.CharField(max_length=64)
    last_name                = models.CharField(max_length=64)
    profile_image            = models.ImageField(
        blank=True, null=True, upload_to='professor_profiles/', validators=[FileSizeValidator(max_mb=4)]
    )

    office_number            = models.CharField(max_length=16, blank=True)
    telegram_account         = models.CharField(max_length=64, blank=True)
    email                    = models.EmailField(unique=True, null=True, blank=True)
    website_url              = models.URLField(blank=True, null=True)

    office_location          = models.CharField(max_length=128, blank=True)
    schedule_image           = models.ImageField(
        blank=True, null=True, upload_to='professor_schedules/', validators=[FileSizeValidator(max_mb=4)]
    )

    student_scores_avg       = RatingAvgField(max_rating=20)
    overall_rating           = RatingAvgField()
    grading_avg              = RatingAvgField()
    general_knowledge_avg    = RatingAvgField()
    teaching_engagement_avg  = RatingAvgField()
    exam_difficulty_avg      = RatingAvgField()
    homework_difficulty_avg  = RatingAvgField()
    average_would_take_again = RatingAvgField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
