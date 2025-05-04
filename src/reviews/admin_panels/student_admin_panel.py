from django.contrib import admin
from src.reviews.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user__username', 'faculty', 'major']
    list_filter = ['faculty', 'major', 'created_at']
