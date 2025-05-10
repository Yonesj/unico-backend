import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from src.reviews.models import Review, Course, Professor, Faculty
from src.accounts.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user_factory(db):
    counter = {'count': 0}

    def create_user(**kwargs):
        count = counter['count']
        counter['count'] += 1
        defaults = {
            'username': f'user_{count}',
            'email': f'user_{count}@example.com',
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        return get_user_model().objects.create_user(**defaults)

    return create_user



@pytest.fixture
def faculty(db):
    return Faculty.objects.create(name="Engineering")


@pytest.fixture
def professor_factory(db, faculty):
    def create_professor(**kwargs):
        defaults = {
            'first_name': 'John',
            'last_name': 'Doe',
            'faculty': faculty,
            'overall_rating': 15.00,
            'grading_avg': 16,
            'general_knowledge_avg': 14,
            'teaching_engagement_avg': 13,
            'exam_difficulty_avg': 12,
            'homework_difficulty_avg': 10,
            'student_scores_avg': 16,
            'average_would_take_again': 17,
        }
        defaults.update(kwargs)
        return Professor.objects.create(**defaults)

    return create_professor


@pytest.fixture
def course_factory(professor_factory):
    def create_course(**kwargs):
        if "professor" not in kwargs:
            kwargs["professor"] = professor_factory()
        defaults = {
            "name": "Test Course",
        }
        defaults.update(kwargs)
        return Course.objects.create(**defaults)

    return create_course


@pytest.fixture
def review_factory(course_factory, user_factory):
    def create_review(**kwargs):
        if "course" not in kwargs:
            kwargs["course"] = course_factory()
        if "user" not in kwargs:
            kwargs["user"] = user_factory()
        defaults = {
            'grading': 5,
            'exam_difficulty': 5,
            'general_knowledge': 5,
            'homework_difficulty': 5,
            'teaching_engagement': 5,
            'attendance_policy': 'not_tracked',
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
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_my_review_list_success(api_client, user_factory, professor_factory, course_factory, review_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)

    professor = professor_factory()
    professor2 = professor_factory()

    course = course_factory(professor=professor)
    course2 = course_factory(professor=professor2)

    r1 = review_factory(user=user, course=course)
    r2 = review_factory(user=user, course=course2)
    other_user_review = review_factory(course=course)
    other_prof_course = course_factory()
    other_prof_review = review_factory(user=user, course=other_prof_course)
    r1.save()
    r2.save()
    url = reverse("retrieve-user-professor-reviews", kwargs={"pk": professor.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    for review in response.data:
        assert "id" in review
        assert "course" in review
        assert "grading" in review
        assert "state" in review


@pytest.mark.django_db
def test_my_review_list_unauthenticated(api_client, professor_factory):
    professor = professor_factory()
    url = reverse("retrieve-user-professor-reviews", kwargs={"pk": professor.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_my_review_list_no_reviews(api_client, user_factory, professor_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)

    professor = professor_factory()
    url = reverse("retrieve-user-professor-reviews", kwargs={"pk": professor.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []