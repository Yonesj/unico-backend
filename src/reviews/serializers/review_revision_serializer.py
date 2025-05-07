from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from src.reviews.models import State, ReviewRevision, Review


class ReviewRevisionCreateSerializer(serializers.ModelSerializer):
    state = serializers.HiddenField(default=State.PENDING)

    class Meta:
        model = ReviewRevision
        fields = [
            'state',
            'grading', 'exam_difficulty', 'general_knowledge', 'homework_difficulty', 'teaching_engagement',
            'exam_resources', 'attendance_policy', 'would_take_again', 'received_score', 'review_text'
        ]

    def validate(self, data):
        review = get_object_or_404(Review, pk=self.context['review_id'])

        if ReviewRevision.objects.filter(review=review, state=State.PENDING).exists():
            raise serializers.ValidationError({
                "review": _("There is already a pending edit for this review")
            })

        data['review'] = review
        return data
