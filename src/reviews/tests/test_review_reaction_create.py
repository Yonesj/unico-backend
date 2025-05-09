import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.reviews.models import ReviewReaction, ReviewReactionChoices, Course, Review, Professor


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    counter = {'value': 0}

    def create_user(**kwargs):
        count = counter['value']
        counter['value'] += 1
        defaults = {
            'username': f'user_{kwargs.get("id", count)}',
            'email': f'user_{kwargs.get("id", count)}@example.com',
        }
        defaults.update(kwargs)
        return get_user_model().objects.create(**defaults)

    return create_user


@pytest.fixture
def student_user(user_factory):
    return user_factory(is_ui_student=True)


@pytest.fixture
def auth_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def non_student_user(user_factory):
    return user_factory(is_ui_student=False)


@pytest.fixture
def professor_factory():
    def create_professor(**kwargs):
        defaults = {'first_name': 'Ali', 'last_name': 'Ahmadi'}
        defaults.update(kwargs)
        return Professor.objects.create(**defaults)
    return create_professor


@pytest.fixture
def course_factory(professor_factory):
    def create_course(**kwargs):
        if 'professor' not in kwargs:
            kwargs['professor'] = professor_factory()
        defaults = {'name': 'Test Course'}
        defaults.update(kwargs)
        return Course.objects.create(**defaults)
    return create_course


@pytest.fixture
def review_factory(course_factory, user_factory):
    def create_review(**kwargs):
        if 'course' not in kwargs:
            kwargs['course'] = course_factory()
        if 'user' not in kwargs:
            kwargs['user'] = user_factory()

        defaults = {
            'grading': 5,
            'exam_difficulty': 5,
            'general_knowledge': 5,
            'homework_difficulty': 5,
            'teaching_engagement': 5,
            'attendance_policy': 'REQUIRED',
            'would_take_again': True,
            'review_text': 'Test review',
            'exam_resources': '',
            'received_score': 18.5,
            'state': 'approved',
        }

        defaults.update(kwargs)
        return Review.objects.create(**defaults)

    return create_review


@pytest.fixture
def review(review_factory, student_user):
    return review_factory(user=student_user)


@pytest.mark.django_db
def test_create_reaction_success(auth_client, review, student_user):
    url = reverse('create-review-reaction', kwargs={'pk': review.id})
    response = auth_client.post(url, data={'value': ReviewReactionChoices.LIKE})

    assert response.status_code == status.HTTP_201_CREATED
    assert ReviewReaction.objects.count() == 1
    reaction = ReviewReaction.objects.first()
    assert reaction.user == student_user
    assert reaction.review == review
    assert reaction.value == ReviewReactionChoices.LIKE


@pytest.mark.django_db
def test_create_reaction_twice(auth_client, review, student_user):
    ReviewReaction.objects.create(user=student_user, review=review, value=ReviewReactionChoices.LIKE)

    url = reverse('create-review-reaction', kwargs={'pk': review.id})
    response = auth_client.post(url, data={'value': ReviewReactionChoices.DISLIKE})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data
    assert ReviewReaction.objects.count() == 1


@pytest.mark.django_db
def test_create_reaction_nonexistent_review(auth_client):
    url = reverse('create-review-reaction', kwargs={'pk': 999999})
    response = auth_client.post(url, data={'value': ReviewReactionChoices.LIKE})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data or 'Review does not exist' in str(response.data)


@pytest.mark.django_db
def test_create_reaction_unauthenticated(api_client, review):
    url = reverse('create-review-reaction', kwargs={'pk': review.id})
    response = api_client.post(url, data={'value': ReviewReactionChoices.LIKE})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ReviewReaction.objects.count() == 0


@pytest.mark.django_db
def test_create_reaction_permission_denied(api_client, non_student_user, review):
    api_client.force_authenticate(user=non_student_user)
    url = reverse('create-review-reaction', kwargs={'pk': review.id})
    response = api_client.post(url, data={'value': ReviewReactionChoices.LIKE})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ReviewReaction.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("value", [100, -999, None])
def test_create_reaction_invalid_value(auth_client, review, value):
    url = reverse('create-review-reaction', kwargs={'pk': review.id})
    data = {}
    if value is not None:
        data['value'] = value

    response = auth_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'value' in response.data
    assert ReviewReaction.objects.count() == 0