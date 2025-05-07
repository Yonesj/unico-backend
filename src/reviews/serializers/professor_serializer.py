from rest_framework import serializers
from src.reviews.models import Professor


class ProfessorSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id', 'profile_image', 'first_name', 'last_name']
        read_only_fields = fields
