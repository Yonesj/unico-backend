import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from src.reviews.models import Faculty

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def faculties():
    return [
        Faculty.objects.create(name="Engineering"),
        Faculty.objects.create(name="Science"),
        Faculty.objects.create(name="Arts"),
    ]

@pytest.mark.django_db
def test_faculty_list_success(api_client, faculties):
    url = reverse("list-faculty")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    returned_names = [f["name"] for f in response.data]
    for faculty in faculties:
        assert faculty.name in returned_names

@pytest.mark.django_db
def test_faculty_list_search(api_client):
    Faculty.objects.create(name="Computer Engineering")
    Faculty.objects.create(name="Mathematics")

    url = reverse("list-faculty")
    response = api_client.get(url, {"search": "computer"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Computer Engineering"

@pytest.mark.django_db
def test_faculty_list_empty(api_client):
    url = reverse("list-faculty")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []

@pytest.mark.django_db
def test_faculty_list_unauthenticated_user(api_client, faculties):
    url = reverse("list-faculty")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(faculties)
