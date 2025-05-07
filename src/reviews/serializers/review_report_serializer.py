from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.reviews.models import ReviewReport, Review


class ReviewReportCreateSerializer(serializers.ModelSerializer):
    reporter = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ReviewReport
        fields = ['reporter', 'reason']

    def validate(self, data):
        try:
            review = Review.objects.get(pk=self.context.get('review_id'))
        except Review.DoesNotExist:
            raise serializers.ValidationError(_('Review does not exist'))

        if ReviewReport.objects.filter(reporter=data['reporter'], review=review).exists():
            raise serializers.ValidationError({'non_field_errors': _('You have already reported this review')})

        data['review'] = review
        return data
