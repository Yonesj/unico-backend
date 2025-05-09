import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from src.reviews.models import Faculty, ProfessorProposal
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='student1', password='testpass', is_ui_student=True)

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def faculty():
    return Faculty.objects.create(name="Engineering")

@pytest.mark.django_db
def test_professor_proposal_create_success(authenticated_client, faculty, user):
    url = reverse("propose-professor")

    payload = {
        "first_name": "Ali",
        "last_name": "Zarei",
        "faculty": faculty.id,
        "proposed_courses": ["Algebra", "Physics"],
        "office_number": "1234",
        "telegram_account": "@alizarei",
        "email": "ali@example.com",
        "website_url": "http://example.com",
        "office_location": "Building A, Room 101",
    }
    response = authenticated_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ProfessorProposal.objects.count() == 1

    proposal = ProfessorProposal.objects.first()
    assert proposal.first_name == payload["first_name"]
    assert proposal.state == "pending"
    assert proposal.submitted_by == user


@pytest.mark.django_db
def test_professor_proposal_create_unauthenticated(api_client, faculty):
    url = reverse("propose-professor")

    payload = {
        "first_name": "Ali",
        "last_name": "Zarei",
        "faculty": faculty.id,
        "proposed_courses": ["Algebra"],
        "email": "ali@example.com",
    }

    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_professor_proposal_create_missing_required_fields(authenticated_client):
    url = reverse("propose-professor")
    response = authenticated_client.post(url, data={}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "first_name" in response.data
    assert "last_name" in response.data
    assert "faculty" in response.data
    assert "proposed_courses" in response.data


@pytest.mark.django_db
def test_professor_proposal_create_empty_courses(authenticated_client, faculty):
    url = reverse("propose-professor")

    payload = {
        "first_name": "Reza",
        "last_name": "Jafari",
        "faculty": faculty.id,
        "proposed_courses": [],
        "email": "reza@example.com"
    }

    response = authenticated_client.post(url, data=payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "proposed_courses" in response.data
