from rest_framework import serializers
from src.courses.models import ClassSession


class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = ['day', 'start', 'end', 'is_problem_solving']
