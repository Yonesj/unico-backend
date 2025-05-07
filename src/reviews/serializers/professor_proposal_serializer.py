from rest_framework import serializers
from src.reviews.models import ProfessorProposal, State


class ProfessorProposalCreateSerializer(serializers.ModelSerializer):
    state = serializers.HiddenField(default=State.PENDING)
    proposed_courses = serializers.ListField(child=serializers.CharField())
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ProfessorProposal
        fields = [
            'state', 'first_name', 'last_name', 'faculty', 'proposed_courses',
            'office_number', 'telegram_account', 'email', 'website_url', 'office_location',
            'profile_image', 'submitted_by'
        ]
