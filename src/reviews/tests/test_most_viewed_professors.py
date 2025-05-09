import pytest
from django.contrib.auth import get_user_model

from src.reviews.models import Professor, Course, ProfessorPageView, Review
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def professor_factory(db):
    counter = {'value': 0}

    def create_professor(**kwargs):
        count = counter['value']
        counter['value'] += 1

        defaults = {
            "first_name": f"First{count}",
            "last_name": f"Last{count}",
            "email": f"prof{count}@example.com",
            "overall_rating": 4.0 + count * 0.1,
        }
        courses = kwargs.pop("courses", [])
        defaults.update(kwargs)
        professor = Professor.objects.create(**defaults)
        professor.courses.set(courses)
        return professor

    return create_professor


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
def course_factory(professor_factory):
    def create_course(**kwargs):
        if 'professor' in kwargs:
            professor = kwargs.pop('professor')
        else:
            professor = professor_factory()

        course = Course.objects.create(professor=professor, **kwargs)
        professor.courses.add(course)
        return course

    return create_course


@pytest.fixture
def view_factory(db):
    def create_view(professor):
        return ProfessorPageView.objects.create(professor=professor)

    return create_view


@pytest.fixture
def review_factory(db, user_factory):
    def create_review(course, user=None, **kwargs):
        if user is None:
            user = user_factory()
        defaults = {
            'user': user,
            'course': course,
            'grading': 3,
            'exam_difficulty': 3,
            'general_knowledge': 3,
            'homework_difficulty': 3,
            'teaching_engagement': 3,
            'would_take_again': True,
        }
        defaults.update(kwargs)
        return Review.objects.create(**defaults)

    return create_review


pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_most_viewed_professors_empty_response(api_client):
    url = reverse("most-viewed-professors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_most_viewed_professors_permissions(api_client):
    url = reverse("most-viewed-professors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_most_viewed_professors_invalid_url(api_client):
    url = reverse("most-viewed-professors") + "invalid/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_most_viewed_professors_returns_top_4(api_client, professor_factory, course_factory, view_factory,
                                              review_factory):
    professors = list(Professor.objects.with_stats())
    courses = [course_factory(professor=prof, name=f"Course {i}") for i, prof in enumerate(professors)]

    for i, prof in enumerate(professors):
        for _ in range(i + 1):
            ProfessorPageView.objects.create(professor=prof)
        for j in range(i):
            review_factory(courses[i])

    url = reverse("most-viewed-professors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data

    expected_order = sorted(
        professors,
        key=lambda p: (p.views_count, p.reviews_count),
        reverse=True
    )[:4]

    returned_ids = [prof["id"] for prof in response.data["results"]]
    expected_ids = [prof.id for prof in expected_order]
    assert returned_ids == expected_ids

    for prof_data in response.data["results"]:
        assert "id" in prof_data
        assert "first_name" in prof_data
        assert "last_name" in prof_data
        assert "overall_rating" in prof_data
        assert "reviews_count" in prof_data


def test_most_viewed_professors_with_limit(api_client, professor_factory, course_factory, view_factory, review_factory):
    professors = [professor_factory() for _ in range(5)]
    courses = [course_factory(professor=prof, name=f"Course {i}") for i, prof in enumerate(professors)]

    for i, prof in enumerate(professors):
        for _ in range(i + 1):
            view_factory(prof)
        for j in range(i):
            review_factory(courses[i])

    url = reverse("most-viewed-professors") + "?limit=3"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert len(response.data["results"]) == 3

    expected_order = sorted(
        professors,
        key=lambda p: (p.page_views.count(), sum(course.reviews.count() for course in p.courses.all())),
        reverse=True
    )[:3]

    returned_ids = [prof["id"] for prof in response.data["results"]]
    expected_ids = [prof.id for prof in expected_order]
    assert returned_ids == expected_ids


@pytest.mark.django_db
def test_most_viewed_professors_with_invalid_limit(api_client):
    url = reverse("most-viewed-professors") + "?limit=abc"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
