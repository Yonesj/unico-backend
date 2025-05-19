import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from src.reviews.models import Review, Course, Professor, Faculty
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


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


@pytest.mark.django_db
def test_retrieve_review_success(api_client, review_factory, professor_factory, course_factory):
    professor = professor_factory(id=61)
    course = course_factory(professor=professor)

    r1 = review_factory(course=course, state='approved')
    r2 = review_factory(course=course, state='approved')
    r1.save()
    r2.save()

    url = f"/professor-reviewer/reviews/{r1.pk}/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == r1.id
    assert response.data["user"] == r1.user.id
    assert response.data["course"]["id"] == course.id
    assert response.data["grading"] == 5
    assert response.data["exam_difficulty"] == 5
    assert response.data["review_text"] == "Test review"


@pytest.mark.django_db
def test_review_with_null_fields(api_client, review_factory, professor_factory, course_factory):
    professor = professor_factory(id=61)
    course = course_factory(professor=professor)

    r1 = review_factory(course=course, state='approved', review_text="")
    r1.save()
    url = f"/professor-reviewer/reviews/{r1.pk}/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == r1.id
    assert response.data["review_text"] == ""


def test_review_course_summary(api_client, review_factory, professor_factory, course_factory):
    professor = professor_factory(id=61)
    course = course_factory(professor=professor)

    r1 = review_factory(course=course, state='approved')
    r2 = review_factory(course=course, state='approved')
    r1.save()
    r2.save()
    url = f"/professor-reviewer/reviews/{r1.pk}/"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "course" in response.data
    assert response.data["course"]["id"] == course.id
    assert response.data["course"]["name"] == "Test Course"
