from rest_framework import serializers
from src.courses.models import Plan
from .coures_serializer import CourseModelSerializer


class PlanSerializer(serializers.ModelSerializer):
    courses = CourseModelSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['name', 'courses']
