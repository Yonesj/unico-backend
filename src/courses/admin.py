from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Course, ClassSession, Exam, Plan


class ClassSessionInline(admin.TabularInline):
    model = ClassSession
    extra = 0
    fields = ['day', 'start', 'end', 'is_problem_solving']
    ordering = ['day']


class ExamInline(admin.StackedInline):
    model = Exam
    extra = 0
    fields = ('date', 'start', 'end')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'course_code',
        'course_name',
        'theory',
        'practical',
        'capacity',
        'get_gender_display',
        'professor_name',
    ]
    list_filter = ['gender']
    search_fields = ['id', 'course_code', 'course_name', 'professor_name']
    ordering = ['course_code']
    inlines = [ClassSessionInline, ExamInline]
    fieldsets = (
        (None, {
            'fields': ('course_code', 'course_name')
        }),
        ('Course Details', {
            'fields': ('theory', 'practical', 'capacity', 'gender', 'professor_name', 'class_location'),
        }),
        ('Additional Information', {
            'classes': ('collapse',),
            'fields': ('prerequisites', 'notes'),
        }),
    )

    def get_gender_display(self, obj):
        # Display the full gender value (e.g., "Both" instead of "B")
        return obj.get_gender_display()
    get_gender_display.short_description = 'Gender'


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        'course',
        'day',
        'start',
        'end',
        'is_problem_solving'
    )
    list_filter = ('day', 'is_problem_solving')
    search_fields = ('course__course_code', 'course__course_name')
    ordering = ('course', 'day', 'start')

    fieldsets = (
        (None, {
            'fields': ('course',)
        }),
        ('Session Details', {
            'fields': ('day', 'start', 'end', 'is_problem_solving')
        }),
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('course', 'date', 'start', 'end')
    list_filter = ('date', 'course')
    search_fields = ('course__course_code', 'course__course_name')
    ordering = ('course', 'date')

    fieldsets = (
        (None, {
            'fields': ('course',)
        }),
        ('Exam Details', {
            'fields': ('date', 'start', 'end')
        }),
    )


User = get_user_model()

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'get_courses']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'user__email']
    ordering = ['-created_at']
    filter_horizontal = ['courses']

    def get_courses(self, obj):
        return ", ".join([course.course_code for course in obj.courses.all()])
    get_courses.short_description = "Courses"
