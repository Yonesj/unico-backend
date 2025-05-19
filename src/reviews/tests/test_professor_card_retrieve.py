from django.urls import reverse
from rest_framework import status
import pytest
from src.reviews.models import Professor, Faculty, Course
from rest_framework.test import APIClient


@pytest.fixture
def faculty():
    return Faculty.objects.create(name="Engineering")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def professor(faculty):
    return Professor.objects.create(
        first_name="Ali",
        last_name="Rezaei",
        faculty=faculty,
        student_scores_avg=15,
        overall_rating=4.2,
        grading_avg=4.0,
        general_knowledge_avg=4.1,
        teaching_engagement_avg=3.9,
        exam_difficulty_avg=3.5,
        homework_difficulty_avg=3.8,
        average_would_take_again=4.3,
    )


@pytest.fixture
def course_factory(professor):
    def create_course(**kwargs):
        kwargs.setdefault("professor", professor)
        return Course.objects.create(**kwargs)

    return create_course


@pytest.mark.django_db
def test_retrieve_professor_card_success(api_client, professor):
    url = reverse("retrieve-professors-comparing", args=[professor.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == professor.id
    assert response.data["first_name"] == professor.first_name
    assert "overall_rating" in response.data
    assert "faculty" in response.data
    assert "courses" in response.data


@pytest.mark.django_db
def test_retrieve_professor_card_not_found(api_client):
    url = reverse("retrieve-professors-comparing", args=[9999])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_professor_card_no_courses(api_client, faculty):
    professor = Professor.objects.create(
        first_name="Mehdi",
        last_name="Safari",
        faculty=faculty,
        student_scores_avg=0,
        overall_rating=0,
        grading_avg=0,
        general_knowledge_avg=0,
        teaching_engagement_avg=0,
        exam_difficulty_avg=0,
        homework_difficulty_avg=0,
        average_would_take_again=0,
    )

    url = reverse("retrieve-professors-comparing", args=[professor.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["courses"] == []
