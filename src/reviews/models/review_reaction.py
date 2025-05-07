from django.db import models
from django.contrib.auth import get_user_model


class ReviewReactionChoices(models.IntegerChoices):
    LIKE    =  1, 'Like'
    DISLIKE = -1, 'Dislike'


class ReviewReaction(models.Model):
    user       = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='review_reactions')
    review     = models.ForeignKey('Review', on_delete=models.CASCADE, related_name='reactions')
    value      = models.SmallIntegerField(choices=ReviewReactionChoices.choices, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review'],
                name='unique_user_review_reaction'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        verb = 'liked' if self.value == ReviewReactionChoices.LIKE else 'disliked'
        return f"{self.user} {verb} review #{self.review.id}"
