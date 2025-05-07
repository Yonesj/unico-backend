from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from src.reviews.models import Course


class CourseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']
        read_only_fields = fields


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'professor', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']
        validators = [
            UniqueTogetherValidator(
                queryset=Course.objects.all(),
                fields=['professor', 'name'],
                message=_("This professor already has a course with that name")
            )
        ]
