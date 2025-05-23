from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction
from django.utils.safestring import mark_safe

from src.reviews.models import ProfessorRevision, State, Course


@admin.register(ProfessorRevision)
class ProfessorRevisionAdmin(admin.ModelAdmin):
    """Admin interface for user-submitted Professor revisions."""
    list_display = (
        'id',
        'professor_link',
        'submitted_by',
        'submitted_at',
        'state',
        'validated_by',
        'validated_at'
    )
    list_filter = ('state', 'faculty', 'submitted_at')
    search_fields = (
        'professor__first_name',
        'professor__last_name',
        'submitted_by__username',
        'email'
    )
    ordering = ('-submitted_at',)

    # Only allow editing the state; everything else is read-only
    readonly_fields = (
        'professor_link',
        'submitted_by',
        'submitted_at',
        'validated_by',
        'validated_at',
        'proposed_courses_table',
        'profile_image_preview',
        'schedule_image_preview'
    )

    fieldsets = (
        (None, {
            'fields': ('professor_link', 'submitted_by', 'submitted_at')
        }),
        ("Proposed Affiliation & Courses", {
            'fields': ('faculty', 'proposed_courses_table')
        }),
        ("Contact & Web Presence", {
            'fields': ('office_number', 'telegram_account', 'email', 'website_url')
        }),
        ("Office Locations & Images", {
            'fields': (
                'office_location',
                'profile_image_preview', 'profile_image',
                'schedule_image_preview', 'schedule_image'
            )
        }),
        ("Moderation", {
            'fields': ('state', 'validated_by', 'validated_at')
        }),
    )

    def professor_link(self, obj):
        url = f"/admin/reviews/professor/{obj.professor_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.professor)

    def proposed_courses_table(self, obj):
        """
        Render an HTML table of Course ID + name for each proposed_course_ids entry.
        """
        if not obj.proposed_course_ids:
            return "(no courses)"

        qs = Course.all_objects.filter(pk__in=obj.proposed_course_ids)
        rows = [
            format_html(
                "<tr><td style='padding:4px'>{}</td><td style='padding:4px'>{}</td></tr>",
                c.pk, c.name
            ) for c in qs
        ]
        table = format_html(
            "<table style='border-collapse:collapse;'><thead>"
            "<tr><th style='border-bottom:1px solid #ccc;padding:4px;'>ID</th>"
            "<th style='border-bottom:1px solid #ccc;padding:4px;'>Name</th></tr></thead>"
            "<tbody>{}</tbody></table>",
            mark_safe("".join(rows))
        )
        return table

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="max-height:150px;" />',
                obj.profile_image.url
            )
        return "(no image)"

    def schedule_image_preview(self, obj):
        if obj.schedule_image:
            return format_html(
                '<img src="{}" style="max-height:200px;" />',
                obj.schedule_image.url
            )
        return "(no schedule)"

    def save_model(self, request, obj, form, change):
        is_approval = (
            change
            and 'state' in form.changed_data
            and obj.state == State.APPROVED
        )

        with transaction.atomic():
            if change and 'state' in form.changed_data:
                obj.validated_by = request.user
                obj.validated_at = timezone.now()

            super().save_model(request, obj, form, change)

            if is_approval:
                prof = obj.professor
                prof_changes = {}

                for field in [
                    'faculty', 'office_number', 'telegram_account',
                    'email', 'website_url', 'office_location',
                    'profile_image', 'schedule_image'
                ]:
                    value = getattr(obj, field)
                    if value not in (None, ''):
                        prof_changes[field] = value

                for field, val in prof_changes.items():
                    setattr(prof, field, val)

                prof.save()
                new_courses = []

                for course_id in obj.proposed_course_ids or []:
                    course = Course.all_objects.get(pk=course_id)

                    if course.professor != prof:
                        new_courses.append(
                            Course.objects.create(
                                name=course.name,
                                faculty=prof.faculty,
                                professor=prof,
                                state=State.PENDING
                            )
                        )

                if new_courses:
                    prof.courses.add(*new_courses)

    professor_link.short_description = "Professor"
    profile_image_preview.short_description = "Profile Image"
    schedule_image_preview.short_description = "Schedule Image"
    proposed_courses_table.short_description = "Proposed Courses"
