from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction

from src.reviews.models import ProfessorProposal, State, Professor, Course


@admin.register(ProfessorProposal)
class ProfessorProposalAdmin(admin.ModelAdmin):
    """Admin interface for faculty/schedule proposals by external users."""
    list_display = (
        'id', 'first_name', 'last_name', 'faculty',
        'state', 'submitted_at', 'submitted_by'
    )
    list_filter = ('state', 'faculty', 'submitted_at')
    search_fields = ('first_name', 'last_name', 'email', 'telegram_account')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'submitted_by', 'validated_by', 'validated_at', 'profile_image_preview', 'proposed_courses_display')

    fieldsets = (
        (None, {
            'fields': ('profile_image_preview',)
        }),
        ("Personal & Affiliation", {
            'fields': ('first_name', 'last_name', 'email', 'faculty')
        }),
        ("Contact & Presence", {
            'fields': ('office_number', 'telegram_account', 'website_url', 'profile_image')
        }),
        ("Office & Courses", {
            'fields': ('office_location', 'proposed_courses_display')
        }),
        ("Proposer", {
            'fields': ('submitted_by', 'submitted_at')
        }),
        ("Moderation", {
            'fields': ('state', 'validated_by', 'validated_at')
        }),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height:150px;">', obj.profile_image.url)
        return "(no image)"

    def proposed_courses_display(self, obj):
        return ", ".join(obj.proposed_courses)

    def save_model(self, request, obj, form, change):
        is_approval = change and 'state' in form.changed_data and obj.state == State.APPROVED

        with transaction.atomic():
            if change and 'state' in form.changed_data:
                obj.validated_by = request.user
                obj.validated_at = timezone.now()
            super().save_model(request, obj, form, change)

            if is_approval:
                prof_defaults = {
                    f: getattr(obj, f) for f in [
                        'first_name', 'last_name', 'faculty', 'office_number', 'telegram_account', 'email',
                        'website_url', 'office_location', 'profile_image'
                    ] if getattr(obj, f) not in (None, '')
                }

                professor= Professor.objects.create(**prof_defaults)

                if obj.proposed_courses:
                    course_objs = []

                    for course_name in obj.proposed_courses:
                        course_obj = Course.objects.create(
                            name=course_name, faculty=obj.faculty, professor=professor
                        )
                        course_objs.append(course_obj)

                    professor.courses.set(course_objs)

    profile_image_preview.short_description = "Uploaded Photo"
    proposed_courses_display.short_description = "Proposed Courses"
