import pytest
from django.contrib.auth import get_user_model
from src.reviews.models import Review, ReviewReaction, Professor, Course
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


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
        }

        optional_defaults = {
            'review_text': 'Test review',
            'exam_resources': '',
            'received_score': 18.5,
            'state': 'approved',
        }

        defaults.update(optional_defaults)
        defaults.update(kwargs)

        return Review.objects.create(**defaults)

    return create_review


@pytest.fixture
def review_reaction_factory(review_factory, user_factory):
    def create_reaction(**kwargs):
        if 'review' not in kwargs:
            kwargs['review'] = review_factory()
        if 'user' not in kwargs:
            kwargs['user'] = user_factory()
        if 'value' not in kwargs:
            kwargs['value'] = 1  # LIKE
        return ReviewReaction.objects.create(**kwargs)

    return create_reaction


@pytest.mark.django_db
def test_list_reactions_success(api_client, user_factory, professor_factory, course_factory, review_factory,
                                review_reaction_factory):
    user = user_factory(username="mehdi")
    prof = professor_factory()
    course = course_factory(professor=prof)
    review = review_factory(course=course, user=user)
    review_reaction = review_reaction_factory(review=review, user=user)

    api_client.force_authenticate(user=user)
    url = reverse('retrieve-my-review-reactions', kwargs={'pk': prof.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == review_reaction.id
    assert response.data[0]["review"] == review.id
    assert response.data[0]["value"] == review_reaction.value


@pytest.mark.django_db
def test_list_reactions_requires_authentication(api_client, professor_factory):
    prof = professor_factory()
    url = reverse('retrieve-my-review-reactions', kwargs={'pk': prof.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_reactions_filtered_by_professor(api_client, user_factory, professor_factory, course_factory,
                                              review_factory, review_reaction_factory):
    user = user_factory()
    prof_1 = professor_factory(first_name="P1")
    prof_2 = professor_factory(first_name="P2")

    course_1 = course_factory(professor=prof_1)
    course_2 = course_factory(professor=prof_2)

    review_1 = review_factory(course=course_1)
    review_2 = review_factory(course=course_2)

    reaction_1 = review_reaction_factory(user=user, review=review_1)
    review_reaction_factory(user=user, review=review_2)

    api_client.force_authenticate(user=user)
    url = reverse('retrieve-my-review-reactions', kwargs={'pk': prof_1.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['review'] == reaction_1.review.id


@pytest.mark.django_db
def test_list_reactions_empty_result(api_client, user_factory, professor_factory):
    user = user_factory()
    prof = professor_factory()

    api_client.force_authenticate(user=user)
    url = reverse('retrieve-my-review-reactions', kwargs={'pk': prof.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_user_only_sees_their_own_reactions(api_client, user_factory, professor_factory, course_factory, review_factory,
                                            review_reaction_factory):
    user1 = user_factory(username='u1')
    user2 = user_factory(username='u2')
    prof = professor_factory()
    course = course_factory(professor=prof)
    review = review_factory(course=course)

    review_reaction_factory(user=user1, review=review)
    review_reaction_factory(user=user2, review=review)

    api_client.force_authenticate(user=user1)
    url = reverse('retrieve-my-review-reactions', kwargs={'pk': prof.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
