from django.db import models


class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    BOTH = 'B', 'Both'


class WeekDay(models.TextChoices):
    SATURDAY = 'sat', 'saturday'
    SUNDAY = 'sun', 'sunday'
    MONDAY = 'mon', 'monday'
    TUESDAY = 'tue', 'tuesday'
    WEDNESDAY = 'wed', 'wednesday'
    THURSDAY = 'thu', 'thursday'
    FRIDAY = 'fri', 'friday'
    NONE = 'non', 'none'


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=255)
    theory = models.CharField(max_length=3)
    practical = models.CharField(max_length=3)
    capacity = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=Gender, default=Gender.BOTH)
    professor_name = models.CharField(max_length=255)
    class_location = models.CharField(max_length=255, blank=True, default="")
    prerequisites = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        self.id = int(self.course_code.replace('_', ''))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"
