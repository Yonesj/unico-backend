import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from src.reviews.models import Professor, Course


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory(professor_factory):
    def create_course(**kwargs):
        if 'professor' not in kwargs:
            kwargs['professor'] = professor_factory()
        return Course.objects.create(**kwargs)

    return create_course


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
            "overall_rating": 4.0,
        }
        courses = kwargs.pop("courses", [])
        defaults.update(kwargs)
        professor = Professor.objects.create(**defaults)
        professor.courses.set(courses)
        return professor

    return create_professor


@pytest.mark.django_db
def test_most_popular_professors_returns_top_4(api_client, professor_factory, course_factory):
    course = course_factory(name="Algorithms")

    professors = [
        professor_factory(
            first_name=f"Prof{i}",
            last_name=f"Last{i}",
            overall_rating=4.0 + i * 0.1,
            courses=[course]
        )
        for i in range(5)
    ]

    url = reverse("most-popular-professors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert len(response.data["results"]) == 4

    returned_ratings = [p.get("overall_rating", 0) for p in response.data["results"]]
    assert returned_ratings == sorted(returned_ratings, reverse=True)

    for prof in response.data["results"]:
        assert "id" in prof
        assert "first_name" in prof
        assert "last_name" in prof
        assert "overall_rating" in prof
        assert isinstance(prof["courses"], list)


@pytest.mark.django_db
def test_most_popular_professors_with_limit_query(api_client, professor_factory):
    for i in range(6):
        professor_factory(
            overall_rating=3.0 + i * 0.1
        )

    url = reverse("most-popular-professors") + "?limit=2"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert response.data["count"] == 6


@pytest.mark.django_db
def test_most_popular_professors_returns_empty_list(api_client):
    url = reverse("most-popular-professors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == []


@pytest.mark.django_db
def test_most_popular_professors_allows_anonymous(api_client):
    url = reverse("most-popular-professors")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
