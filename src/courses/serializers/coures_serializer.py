from rest_framework import serializers
from src.courses.models import Course
from .exam_serializer import ExamSerializer
from .class_session_serializer import ClassSessionSerializer


class CourseModelSerializer(serializers.ModelSerializer):
    classes = ClassSessionSerializer(many=True, read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'theory', 'practical', 'capacity', 'gender', 'professor_name',
            'class_location', 'prerequisites', 'notes', 'classes', 'exam'
        ]


class CourseOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    course_code = serializers.CharField()
    course_name = serializers.CharField()
    theory = serializers.CharField()
    practical = serializers.CharField()
    capacity = serializers.IntegerField()
    gender = serializers.CharField()
    professor_name = serializers.CharField()
    class_location = serializers.CharField(required=False, allow_blank=True)
    prerequisites = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    classes = ClassSessionSerializer(many=True)
    exam = ExamSerializer(required=False, allow_null=True)
