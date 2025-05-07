from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models

from src.reviews.models import State
from src.utill.validators import FileSizeValidator


class ProfessorProposal(models.Model):
    first_name         = models.CharField(max_length=50)
    last_name          = models.CharField(max_length=50)
    faculty            = models.ForeignKey('Faculty', on_delete=models.SET_NULL, null=True)
    proposed_courses   = ArrayField(models.CharField(max_length=64), default=list)
    office_number      = models.CharField(max_length=16, blank=True)
    telegram_account   = models.CharField(max_length=64, blank=True)
    email              = models.EmailField(unique=True, null=True, blank=True)
    website_url        = models.URLField(blank=True)
    office_location    = models.CharField(max_length=100, blank=True)
    profile_image      = models.ImageField(upload_to='proposals/', blank=True, null=True, validators=[FileSizeValidator])

    state              = models.CharField(max_length=8, choices=State.choices, default=State.PENDING)
    validated_by       = models.ForeignKey(get_user_model(), null=True, blank=True,
                                           on_delete=models.SET_NULL, related_name='+')
    validated_at       = models.DateTimeField(null=True, blank=True)
    submitted_at       = models.DateTimeField(auto_now_add=True)
    submitted_by       = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ['-submitted_at']
