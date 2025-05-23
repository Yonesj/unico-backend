from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from src.reviews.models import Review, State
from src.reviews.serializers import CourseSummarySerializer, ProfessorSummarySerializer


class ReviewRetrieveSerializer(serializers.ModelSerializer):
    course = CourseSummarySerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    overall = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'course', 'created_at',
            'grading', 'exam_difficulty', 'general_knowledge', 'homework_difficulty', 'teaching_engagement',
            'would_take_again', 'attendance_policy', 'received_score', 'exam_resources',
            'review_text', 'likes_count', 'dislikes_count', 'overall'
        ]
        read_only_fields = fields

    def get_overall(self, obj):
        metrics = ['grading', 'exam_difficulty', 'general_knowledge', 'homework_difficulty', 'teaching_engagement']
        values = []

        for m in metrics:
            val = getattr(obj, m, None)
            if val is not None:
                values.append(val)

        if not values:
            return None

        return round(sum(values) / len(values), 1)

class MyReviewRetrieveSerializer(ReviewRetrieveSerializer):
    class Meta(ReviewRetrieveSerializer.Meta):
        fields = list(ReviewRetrieveSerializer.Meta.fields) + ['state']


class ReviewCardSerializer(serializers.ModelSerializer):
    professor = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'review_text', 'professor']
        read_only_fields = fields

    def get_professor(self, obj):
        return ProfessorSummarySerializer(obj.course.professor).data


class ReviewCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    state = serializers.HiddenField(default=State.PENDING)
    would_take_again = serializers.BooleanField(required=True)

    class Meta:
        model = Review
        fields = [
            'user', 'course', 'state',
            'grading', 'exam_difficulty', 'general_knowledge', 'homework_difficulty', 'teaching_engagement',
            'exam_resources', 'attendance_policy', 'would_take_again', 'received_score', 'review_text'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['user', 'course'],
                message=_("You have already submitted a review for this course")
            )
        ]

    def validate(self, attrs):
        user = attrs.get('user')
        course = attrs.get('course')

        if Review.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError({
                'non_field_errors': [_("You have already submitted a review for this course")]
            })

        return super().validate(attrs)

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                'non_field_errors': [_("You have already submitted a review for this course")]
            })
