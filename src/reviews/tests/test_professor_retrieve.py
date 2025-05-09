import pytest
from django.urls import reverse
from rest_framework import status
from src.reviews.models import ProfessorPageView , Professor ,Faculty


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


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
def professor(professor_factory):
    return professor_factory()


@pytest.mark.django_db
def test_retrieve_professor_success(api_client, professor):
    url = reverse("retrieve-professor", args=[professor.id])

    response = api_client.get(url, HTTP_USER_AGENT="pytest-agent")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == professor.id
    assert data["first_name"] == professor.first_name
    assert data["last_name"] == professor.last_name
    assert isinstance(data["reviews_count"], int)
    assert "related_professors" in data

    assert ProfessorPageView.objects.filter(professor=professor).exists()
    view = ProfessorPageView.objects.get(professor=professor)
    assert view.user_agent == "pytest-agent"


@pytest.mark.django_db
def test_retrieve_professor_not_found(api_client):
    url = reverse("retrieve-professor", args=[9999])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_professor_unauthenticated(api_client, professor):
    url = reverse("retrieve-professor", args=[professor.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_related_professors_fallback(monkeypatch, api_client, professor):

    monkeypatch.setattr(Professor.objects, "related_by_courses", lambda prof_id: Professor.objects.none())
    monkeypatch.setattr(Professor.objects, "in_same_faculty", lambda prof: Professor.objects.filter(id=prof.id))

    url = reverse("retrieve-professor", args=[professor.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.json()["related_professors"]) == 1
