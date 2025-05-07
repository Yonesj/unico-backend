from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.reviews.models import State
from src.reviews.models.professor_revision import ProfessorRevision


class ProfessorRevisionCreateSerializer(serializers.ModelSerializer):
    submitted_by     = serializers.HiddenField(default=serializers.CurrentUserDefault())
    state            = serializers.HiddenField(default=State.PENDING)
    proposed_courses = serializers.ListField(
        child=serializers.CharField(max_length=64),
        help_text="List of the professor's course names (will replace existing when approved)",
        allow_empty=True
    )

    class Meta:
        model = ProfessorRevision
        fields = [
            'professor', 'submitted_by', 'state',
            'faculty', 'proposed_courses',
            'office_number', 'telegram_account',
            'email', 'website_url', 'office_location',
            'profile_image', 'schedule_image',
        ]
        read_only_fields = ['state', 'submitted_at']

    def validate(self, attrs):
        prof     = attrs['professor']
        user     = attrs['submitted_by']

        if ProfessorRevision.objects.filter(professor=prof, submitted_by=user, state=State.PENDING).exists():
            raise serializers.ValidationError(_("You already have a pending revision for this professor."))

        return attrs
