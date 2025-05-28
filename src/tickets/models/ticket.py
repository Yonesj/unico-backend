from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models


class TicketStatus(models.TextChoices):
    CLOSED = "close", "بسته شده"
    OPEN = "open", "در حال برسی"
    ANSWERED = "answered", "پاسخ داده شده"


class TicketSubject(models.TextChoices):
    FINANCIAL = "financial", "مالی"
    TECHNICAL = "technical", "فنی"
    SUGGESTION = "suggestion", "پیشنهادات و انتقادات"
    ADVERTISEMENT = "advertisement", "تبلیغات"


class TicketUnit(models.TextChoices):
    NONE = "none", "هیچکدام"
    COURSE_SCHEDULER = "courses", "انتخاب واحد"
    PROFESSOR_REVIEWER = "professors", "نظرسنجی اساتید"
    NOTIFICATION = "notifications", "اطلاع‌رسانی‌"


class Ticket(models.Model):
    uid = models.UUIDField(default=uuid4, editable=False, unique=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=128)

    status = models.CharField(max_length=8, choices=TicketStatus.choices, db_index=True, default=TicketStatus.OPEN)
    subject = models.CharField(max_length=16, choices=TicketSubject.choices, db_index=True)
    unit = models.CharField(max_length=16, choices=TicketUnit.choices, db_index=True, default=TicketUnit.NONE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()}) - {self.user.username}"
