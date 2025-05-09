import pytest
from rest_framework import status
from django.urls import reverse

from src.accounts.models import User
from src.reviews.models import Professor, Faculty, ProfessorRevision
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()
@pytest.fixture
def professor(faculty):
    return Professor.objects.create(
        faculty=faculty,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        student_scores_avg=18,
        overall_rating=4,
        grading_avg=4,
        general_knowledge_avg=4,
        teaching_engagement_avg=4,
        exam_difficulty_avg=3,
        homework_difficulty_avg=3,
        average_would_take_again=4,
    )



@pytest.fixture
def faculty():
    return Faculty.objects.create(name="Engineering")


@pytest.fixture
def user(db):
    return User.objects.create_user(username='student1', password='testpass', is_ui_student=True)


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
def test_professor_revision_create_success(authenticated_client, professor, faculty, user):
    url = reverse('edit-professor', kwargs={'pk': professor.pk})

    payload = {
        "professor": professor.id,
        "faculty": faculty.id,
        "proposed_courses": ["Advanced Algebra", "Quantum Mechanics"],
        "office_number": "12345",
        "telegram_account": "@john_doe",
        "email": "john.doe@example.com",
        "website_url": "http://johndoe.com",
        "office_location": "Room 101",
    }

    response = authenticated_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ProfessorRevision.objects.count() == 1

    revision = ProfessorRevision.objects.first()
    assert revision.professor == professor
    assert revision.state == "pending"
    assert revision.submitted_by == user


@pytest.mark.django_db
def test_professor_revision_create_duplicate_request(authenticated_client, professor, faculty, user):
    ProfessorRevision.objects.create(
        professor=professor,
        faculty=faculty,
        proposed_courses=["Algebra", "Physics"],
        submitted_by=user
    )

    url = reverse('edit-professor', kwargs={'pk': professor.pk})

    payload = {
        "professor": professor.id,
        "faculty": faculty.id,
        "proposed_courses": ["Advanced Algebra", "Quantum Mechanics"],
        "office_number": "12345",
        "telegram_account": "@john_doe",
        "email": "john.doe@example.com",
        "website_url": "http://johndoe.com",
        "office_location": "Room 101",
    }

    response = authenticated_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'professor' in response.data['non_field_errors'][0].lower()


@pytest.mark.django_db
def test_professor_revision_create_missing_required_fields(authenticated_client, professor, faculty, user):
    url = reverse('edit-professor', kwargs={'pk': professor.pk})

    payload = {
        "professor": professor.id,
        "faculty": faculty.id,
        "proposed_courses": [],
    }

    response = authenticated_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert 'proposed_courses' in response.data
    assert 'office_number' in response.data


@pytest.mark.django_db
def test_professor_revision_create_unauthorized(api_client, professor, faculty):
    url = reverse('edit-professor', kwargs={'pk': professor.pk})

    payload = {
        "professor": professor.id,
        "faculty": faculty.id,
        "proposed_courses": ["Advanced Algebra", "Quantum Mechanics"],
        "office_number": "12345",
        "telegram_account": "@john_doe",
        "email": "john.doe@example.com",
        "website_url": "http://johndoe.com",
        "office_location": "Room 101",
    }

    response = api_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data


@pytest.mark.django_db
def test_professor_revision_create_empty_proposed_courses(authenticated_client, professor, faculty, user):
    url = reverse('edit-professor', kwargs={'pk': professor.pk})

    payload = {
        "professor": professor.id,
        "faculty": faculty.id,
        "proposed_courses": [],
        "office_number": "12345",
        "telegram_account": "@john_doe",
        "email": "john.doe@example.com",
        "website_url": "http://johndoe.com",
        "office_location": "Room 101",
    }

    response = authenticated_client.post(url, data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    revision = ProfessorRevision.objects.first()
    assert revision.proposed_courses == []
