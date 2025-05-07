from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class RatingAvgField(models.DecimalField):
    """
    A custom model field for average ratings that automatically applies
    validators to ensure values lie between 0 and `max_rating`.

    Usage:
        average_rating = RatingAvgField(max_rating=5)
    """

    def __init__(self, max_rating=5, **kwargs):
        self.max_rating = max_rating

        kwargs.setdefault('max_digits', 4)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('null', True)
        kwargs.setdefault('blank', True)

        validators = list(kwargs.get('validators', []))
        validators.append(MinValueValidator(0))
        validators.append(MaxValueValidator(self.max_rating))
        kwargs['validators'] = validators

        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        path = 'src.reviews.fields.RatingAvgField'

        if self.max_rating != 5:
            kwargs['max_rating'] = self.max_rating

        kwargs.pop('validators', None)
        return name, path, args, kwargs
