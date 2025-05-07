from django.contrib import admin
from django.utils.html import format_html

from src.reviews.models import Professor, Course


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ('name', 'faculty', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = (
         'id', 'profile_thumb', 'first_name', 'last_name', 'email', 'faculty', 'overall_rating'
    )
    list_display_links = ['first_name', 'last_name', 'email']
    list_filter = ['faculty']
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('faculty', 'last_name')
    inlines = [CourseInline]

    readonly_fields = (
        'profile_image_preview',
        'student_scores_avg', 'overall_rating',
        'grading_avg', 'general_knowledge_avg', 'teaching_engagement_avg',
        'exam_difficulty_avg', 'homework_difficulty_avg', 'average_would_take_again'
    )

    fieldsets = (
        (None, {
            'fields': ('profile_image_preview', 'profile_image')
        }),
        ("Basic Information", {
            'fields': ('first_name', 'last_name', 'email', 'faculty')
        }),
        ("Online Presence & Contact", {
            'fields': ('telegram_account', 'website_url', 'office_number')
        }),
        ("Office Details", {
            'fields': ('office_location', 'schedule_image')
        }),
        ("Ratings (read-only)", {
            'fields': (
                'student_scores_avg', 'overall_rating',
                'grading_avg', 'general_knowledge_avg', 'teaching_engagement_avg',
                'exam_difficulty_avg', 'homework_difficulty_avg', 'average_would_take_again'
            )
        }),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.profile_image.url)
        return "(No image)"

    def profile_thumb(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="height:25px; width:25px;"/>', obj.profile_image.url)
        return "-"

    profile_image_preview.short_description = 'Profile Image Preview'
    profile_thumb.short_description = 'Thumb'
    profile_thumb.allow_tags = True
