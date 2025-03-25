from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model


User = get_user_model()

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
    theory = models.PositiveSmallIntegerField()
    practical = models.PositiveSmallIntegerField()
    capacity = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=1, choices=Gender, default=Gender.BOTH)
    professor_name = models.CharField(max_length=255)
    class_location = models.CharField(max_length=255, null=True, blank=True)
    prerequisites = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    notes = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        self.id = int(self.course_code.replace('_', ''))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"


class ClassSession(models.Model):
    course = models.ForeignKey(Course, related_name="classes", on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=WeekDay, default=WeekDay.NONE)
    start = models.PositiveSmallIntegerField()
    end = models.PositiveSmallIntegerField()


class Exam(models.Model):
    course = models.OneToOneField(Course, related_name="exam", on_delete=models.CASCADE)
    date = models.DateField()
    start = models.PositiveSmallIntegerField()
    end = models.PositiveSmallIntegerField()


class Plan(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    courses = models.ManyToManyField(Course, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
