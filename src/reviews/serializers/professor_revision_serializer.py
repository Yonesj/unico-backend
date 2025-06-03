from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from src.reviews.models import State, Professor, Course
from src.reviews.models.professor_revision import ProfessorRevision


class ProfessorRevisionCreateSerializer(serializers.ModelSerializer):
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    state = serializers.HiddenField(default=State.PENDING)
    website_url = serializers.CharField(required=False, allow_blank=True)
    proposed_course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = ProfessorRevision
        fields = [
            'submitted_by', 'state',
            'faculty', 'proposed_course_ids',
            'office_number', 'telegram_account',
            'email', 'website_url', 'office_location',
            'profile_image', 'schedule_image',
        ]
        read_only_fields = ['state', 'submitted_at']

    def validate_proposed_course_ids(self, value):
        unique_ids = set(value)
        existing_ids = set(
            Course.all_objects
            .filter(pk__in=unique_ids)
            .values_list('pk', flat=True)
        )
        missing = unique_ids - existing_ids

        if missing:
            raise serializers.ValidationError(
                '\n'.join([_(f"Course with id {i} does not exist.") for i in sorted(missing)])
            )

        return list(unique_ids)

    def validate_website_url(self, value):
        if not value:
            return value

        if not value.lower().startswith(("http://", "https://", "ftp://")):
            value = "http://" + value

        validator = URLValidator()
        try:
            validator(value)
        except DjangoValidationError:
            raise serializers.ValidationError(_("Enter a valid URL."))

        return value

    def validate(self, attrs):
        try:
            prof = Professor.objects.get(pk=self.context["professor_id"])
            attrs['professor'] = prof
        except Professor.DoesNotExist:
            raise serializers.ValidationError(_("Professor does not exist"))

        user = attrs['submitted_by']

        if ProfessorRevision.objects.filter(professor=prof, submitted_by=user, state=State.PENDING).exists():
            raise serializers.ValidationError(_("You already have a pending revision for this professor."))

        return attrs
