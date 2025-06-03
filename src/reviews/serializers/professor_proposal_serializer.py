from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from src.reviews.models import ProfessorProposal, State, Faculty


class ProfessorProposalCreateSerializer(serializers.ModelSerializer):
    state = serializers.HiddenField(default=State.PENDING)
    proposed_courses = serializers.ListField(child=serializers.CharField())
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    website_url = serializers.CharField(required=False, allow_blank=True)
    faculty = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.all(),
        required=True
    )

    class Meta:
        model = ProfessorProposal
        fields = [
            'state', 'first_name', 'last_name', 'faculty', 'proposed_courses',
            'office_number', 'telegram_account', 'email', 'website_url', 'office_location',
            'profile_image', 'submitted_by'
        ]

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
