from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import transaction
from django import forms

from src.reviews.models import ProfessorRevision, State, professor, Course


class ProfessorRevisionForm(forms.ModelForm):
    # render the list of strings as a textarea (one course per line)
    proposed_courses = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        help_text="Enter one course name per line."
    )

    class Meta:
        model = ProfessorRevision
        fields = '__all__'

    def clean_proposed_courses(self):
        raw = self.cleaned_data.get('proposed_courses', '')
        # Split on newlines, strip out empty lines
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def initial_proposed_courses(self):
        # For displaying existing data in the textarea
        return "\n".join(self.instance.proposed_courses or [])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prepopulate the textarea from the model’s list
        if self.instance and self.instance.proposed_courses:
            self.fields['proposed_courses'].initial = "\n".join(self.instance.proposed_courses)


@admin.register(ProfessorRevision)
class ProfessorRevisionAdmin(admin.ModelAdmin):
    """Admin interface for user-submitted Professor revisions."""
    form = ProfessorRevisionForm
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
        'proposed_courses_display',
        'profile_image_preview',
        'schedule_image_preview'
    )

    fieldsets = (
        (None, {
            'fields': ('professor_link', 'submitted_by', 'submitted_at')
        }),
        ("Proposed Affiliation & Courses", {
            'fields': ('faculty', 'proposed_courses_display', 'proposed_courses')
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

    def proposed_courses_display(self, obj):
        return ", ".join(obj.proposed_courses) or "(none)"

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

                prof_defaults = {
                    field: getattr(obj, field)
                    for field in [
                        'first_name', 'last_name', 'faculty',
                        'office_number', 'telegram_account',
                        'email', 'website_url', 'office_location',
                        'profile_image', 'schedule_image'
                    ]
                    if getattr(obj, field) not in (None, '')
                }

                for field, val in prof_defaults.items():
                    setattr(prof, field, val)

                prof.save()
                new_courses = []

                for course_name in obj.proposed_courses or []:
                    if not Course.objects.filter(name=course_name, professor=prof).exists():
                        new_courses.append(
                            Course.objects.create(
                                name=course_name,
                                faculty=obj.faculty,
                                professor=prof
                            )
                        )

                if new_courses:
                    prof.courses.add(*new_courses)

    professor_link.short_description = "Professor"
    profile_image_preview.short_description = "Profile Image"
    schedule_image_preview.short_description = "Schedule Image"
    proposed_courses_display.short_description = "Proposed Courses"
