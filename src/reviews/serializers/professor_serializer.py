from rest_framework import serializers
from src.reviews.models import Professor
from src.reviews.serializers import CourseSummarySerializer


class ProfessorSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id', 'profile_image', 'first_name', 'last_name', 'overall_rating']
        read_only_fields = fields


class ProfessorRetrieveSerializer(serializers.ModelSerializer):
    courses = CourseSummarySerializer(many=True, read_only=True)
    faculty = serializers.StringRelatedField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    related_professors = serializers.SerializerMethodField()

    class Meta:
        model = Professor
        fields = [
            'id', 'overall_rating', 'reviews_count',
            'profile_image', 'first_name', 'last_name', 'faculty', 'courses',
            'office_number', 'telegram_account', 'email', 'website_url', 'office_location', 'schedule_image',
            'student_scores_avg', 'average_would_take_again', 'related_professors',
            'grading_avg', 'general_knowledge_avg', 'teaching_engagement_avg', 'exam_difficulty_avg', 'homework_difficulty_avg',
        ]
        read_only_fields = fields

    def get_related_professors(self, prof):
        qs = Professor.objects.related_by_courses(prof.id)

        if not qs.exists():
            qs = Professor.objects.in_same_faculty(prof)

        return ProfessorSummarySerializer(qs, many=True).data


class ProfessorSearchResultSerializer(serializers.ModelSerializer):
    courses = CourseSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Professor
        fields = [
            'id',
            'first_name',
            'last_name',
            'profile_image',
            'courses'
        ]
        read_only_fields = fields


class ProfessorCardSerializer(serializers.ModelSerializer):
    courses = CourseSummarySerializer(many=True, read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Professor
        fields = [
            'id',
            'first_name',
            'last_name',
            'profile_image',
            'overall_rating',
            'reviews_count',
            'courses'
        ]
        read_only_fields = fields


class ProfessorCompareSerializer(serializers.ModelSerializer):
    courses = CourseSummarySerializer(many=True, read_only=True)
    faculty = serializers.StringRelatedField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Professor
        fields = [
            'id', 'overall_rating', 'reviews_count',
            'first_name', 'last_name', 'faculty', 'courses',
            'grading_avg', 'general_knowledge_avg', 'teaching_engagement_avg', 'exam_difficulty_avg', 'homework_difficulty_avg',
            'student_scores_avg', 'average_would_take_again',
        ]
        read_only_fields = fields
