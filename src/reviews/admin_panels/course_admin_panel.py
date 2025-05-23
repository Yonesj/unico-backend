from django.utils import timezone
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
    list_display = ['id', 'faculty' ,'name', 'professor', 'created_at', 'state']
    list_filter = ['faculty', 'state']
    list_display_links = ['name']
    search_fields = ['name', 'professor__first_name', 'professor__last_name']
    ordering = ['name', 'created_at']
    inlines = [ReviewInline]

    def get_queryset(self, request):
        return self.model.all_objects.select_related('professor', 'faculty')

    def save_model(self, request, obj, form, change):
        if change and 'state' in form.changed_data:
            obj.validated_by = request.user
            obj.validated_at = timezone.now()
        super().save_model(request, obj, form, change)
