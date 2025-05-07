from django.contrib import admin
from src.reviews.models import Course, Review


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'course', 'created_at', 'state')
    readonly_fields = ['created_at']
    can_delete = False
    show_change_link = True
    ordering = ['-created_at']
    classes = ['collapse']
    page_size = 25


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'faculty' ,'name', 'professor', 'created_at']
    list_filter = ['faculty']
    list_display_links = ['name']
    search_fields = ['name', 'professor__first_name', 'professor__last_name']
    ordering = ['name', 'created_at']
    inlines = [ReviewInline]
