from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RatingField(models.PositiveSmallIntegerField):
    """
    A custom model field for ratings that automatically applies
    validators to ensure values lie between 0 and `max_rating`.

    Usage:
        average_rating = RatingField(max_rating=5)
    """

    def __init__(self, max_rating=5, **kwargs):
        self.max_rating = max_rating

        kwargs.setdefault('null', False)
        kwargs.setdefault('blank', False)

        validators = list(kwargs.get('validators', []))
        validators.append(MinValueValidator(0))
        validators.append(MaxValueValidator(self.max_rating))
        kwargs['validators'] = validators

        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        path = 'src.reviews.fields.RatingField'

        if self.max_rating != 5:
            kwargs['max_rating'] = self.max_rating

        kwargs.pop('validators', None)
        return name, path, args, kwargs
