import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
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
        }
        courses = kwargs.pop("courses", [])
        defaults.update(kwargs)
        professor = Professor.objects.create(**defaults)
        professor.courses.set(courses)
        return professor

    return create_professor


@pytest.mark.django_db
def test_professor_list_returns_all(api_client, professor_factory):
    prof1 = professor_factory(first_name="John", last_name="Smith")
    prof2 = professor_factory(first_name="Jane", last_name="Doe")

    url = reverse("list-professor")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    names = [f"{item['first_name']} {item['last_name']}" for item in response.data]
    assert "John Smith" in names
    assert "Jane Doe" in names


@pytest.mark.django_db
def test_professor_list_search_by_name(api_client, professor_factory):
    prof1 = professor_factory(first_name="Ali", last_name="Karimi")
    prof2 = professor_factory(first_name="Sara", last_name="Mousavi")

    url = reverse("list-professor")
    response = api_client.get(url, data={"search": "Karimi"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['last_name'] == "Karimi"


@pytest.mark.django_db
def test_professor_list_search_by_course(api_client, professor_factory, course_factory):
    math = course_factory(name="Math")
    prof = professor_factory(first_name="Alan", last_name="Turing", courses=[math])

    url = reverse("list-professor")
    response = api_client.get(url, data={"search": "Math"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['last_name'] == "Turing"
    assert response.data[0]['courses'][0]['name'] == "Math"


@pytest.mark.django_db
def test_professor_list_empty_when_no_match(api_client, professor_factory):
    professor_factory(first_name="Mehdi", last_name="Rezaei")

    url = reverse("list-professor")
    response = api_client.get(url, data={"search": "Nonexistent"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_professor_list_empty_when_no_professors(api_client):
    url = reverse("list-professor")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
