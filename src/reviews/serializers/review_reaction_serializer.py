from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from src.reviews.models import ReviewReaction, Review


class ReviewReactionRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReaction
        fields = ['id', 'review', 'value']
        read_only_fields = fields


class ReviewReactionCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ReviewReaction
        fields = ['user', 'value']

    def validate(self, data):
        try:
            review = Review.objects.get(pk=self.context['review_id'])
        except Review.DoesNotExist:
            raise serializers.ValidationError(_("Review does not exist"))

        if ReviewReaction.objects.filter(user=data['user'], review=review).exists():
            raise serializers.ValidationError({
                'non_field_errors': [_("You’ve already reacted to this review")]
            })

        data['review'] = review
        return data


class ReviewReactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReaction
        fields = ['value']
