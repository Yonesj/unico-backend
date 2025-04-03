from rest_framework import serializers
from src.courses.models import Exam


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['date', 'start', 'end']
