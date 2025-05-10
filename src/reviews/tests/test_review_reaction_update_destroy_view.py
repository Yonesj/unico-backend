import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.reviews.models import Review, ReviewReaction, ReviewReactionChoices, Course, Professor


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
    return user_factory(username="student", is_ui_student=True)


@pytest.fixture
def another_user(user_factory):
    return user_factory(username="another")


@pytest.fixture
def auth_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def another_auth_client(api_client, another_user):
    api_client.force_authenticate(user=another_user)
    return api_client


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
def review_factory(course_factory, student_user):
    def create_review(**kwargs):
        defaults = {
            'course': course_factory(),
            'user': student_user,
            'grading': 5,
            'exam_difficulty': 5,
            'general_knowledge': 5,
            'homework_difficulty': 5,
            'teaching_engagement': 5,
            'attendance_policy': 'REQUIRED',
            'would_take_again': True,
            'state': 'approved',
        }
        defaults.update(kwargs)
        return Review.objects.create(**defaults)

    return create_review


@pytest.fixture
def review_reaction_factory(review_factory, student_user):
    def create_reaction(**kwargs):
        if 'review' not in kwargs:
            kwargs['review'] = review_factory()
        if 'user' not in kwargs:
            kwargs['user'] = student_user
        if 'value' not in kwargs:
            kwargs['value'] = ReviewReactionChoices.LIKE
        return ReviewReaction.objects.create(**kwargs)

    return create_reaction


@pytest.mark.django_db
def test_patch_review_reaction_success(auth_client, review_reaction_factory):
    reaction = review_reaction_factory(value=ReviewReactionChoices.LIKE)
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = auth_client.patch(url, data={'value': ReviewReactionChoices.DISLIKE})
    reaction.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert reaction.value == ReviewReactionChoices.DISLIKE


@pytest.mark.django_db
def test_delete_review_reaction_success(auth_client, review_reaction_factory):
    reaction = review_reaction_factory()
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ReviewReaction.objects.filter(id=reaction.id).exists()


@pytest.mark.django_db
def test_patch_permission_denied_for_non_owner(another_auth_client, review_reaction_factory):
    reaction = review_reaction_factory()
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = another_auth_client.patch(url, data={'value': ReviewReactionChoices.DISLIKE})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_permission_denied_for_non_owner(another_auth_client, review_reaction_factory):
    reaction = review_reaction_factory()
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = another_auth_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_patch(api_client, review_reaction_factory):
    reaction = review_reaction_factory()
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = api_client.patch(url, data={'value': ReviewReactionChoices.DISLIKE})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_with_invalid_value(auth_client, review_reaction_factory):
    reaction = review_reaction_factory()
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = auth_client.patch(url, data={'value': 999})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'value' in response.data


@pytest.mark.django_db
def test_patch_with_missing_value(auth_client, review_reaction_factory):
    reaction = review_reaction_factory()
    url = reverse('update-delete-review-reaction', kwargs={'pk': reaction.pk})

    response = auth_client.patch(url, data={})

    assert response.status_code == status.HTTP_200_OK
    assert 'value' in response.data


@pytest.mark.django_db
def test_patch_nonexistent_reaction(auth_client):
    url = reverse('update-delete-review-reaction', kwargs={'pk': 9999})

    response = auth_client.patch(url, data={'value': ReviewReactionChoices.LIKE})

    assert response.status_code == status.HTTP_404_NOT_FOUND
