from rest_framework import serializers

from src.courses.models import Course, ClassSession, Exam, Plan


class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = ['day', 'start', 'end']


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['date', 'start', 'end']


class CourseSerializer(serializers.ModelSerializer):
    classes = ClassSessionSerializer(many=True, read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'course_code', 'course_name', 'theory', 'practical', 'capacity', 'gender', 'professor_name',
            'class_location', 'prerequisites', 'notes', 'classes', 'exam'
        ]


class PlanSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['name', 'courses']


class GolestanRequestSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    password = serializers.CharField()
