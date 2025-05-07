from rest_framework import serializers
from src.reviews.models import Faculty


class FacultyRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name']
