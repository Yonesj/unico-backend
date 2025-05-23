from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.reviews.models import Course, State


class CourseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name']
        read_only_fields = fields


class CourseCreateSerializer(serializers.ModelSerializer):
    state = serializers.HiddenField(default=State.PENDING)

    class Meta:
        model = Course
        fields = ['id', 'professor', 'name', 'state']
        read_only_fields = ['id']

    def validate(self, attrs):
        professor = attrs.get('professor')
        name = attrs.get('name')

        if Course.objects.filter(state=State.APPROVED, professor=professor, name=name).exists():
            raise serializers.ValidationError({
                'non_field_errors': [_("This professor already has a course with that name")]
            })

        attrs['faculty'] = professor.faculty
        return super().validate(attrs)
