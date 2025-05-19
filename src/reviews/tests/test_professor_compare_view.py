import pytest
from src.reviews.models import Professor, Faculty ,Course
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()



@pytest.fixture
def faculty():
    return Faculty.objects.create(name="Engineering")



@pytest.fixture
def professor_factory(faculty):
    def create_professor(**kwargs):
        defaults = {
            "first_name": "Ali",
            "last_name": "Rezaei",
            "faculty": faculty,
            "student_scores_avg": 15,
            "overall_rating": 4.2,
            "grading_avg": 4.0,
            "general_knowledge_avg": 4.1,
            "teaching_engagement_avg": 3.9,
            "exam_difficulty_avg": 3.5,
            "homework_difficulty_avg": 3.8,
            "average_would_take_again": 4.3,
        }
        defaults.update(kwargs)
        return Professor.objects.create(**defaults)

    return create_professor


@pytest.fixture
def course_factory():
    def create_course(**kwargs):
        return Course.objects.create(**kwargs)

    return create_course


@pytest.mark.django_db
def test_professor_compare_success(api_client, professor_factory):
    professor = professor_factory(first_name="Sara", last_name="Ahmadi")

    url = reverse("compare-professors")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == professor.id
    assert response.data[0]["first_name"] == "Sara"
    assert "courses" in response.data[0]


@pytest.mark.django_db
def test_professor_compare_with_search_by_name(api_client, professor_factory):
    professor_factory(first_name="Sara")
    professor_factory(first_name="Ali")

    url = reverse("compare-professors") + "?search=Sara"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["first_name"] == "Sara"


@pytest.mark.django_db
def test_professor_compare_with_search_by_course(api_client, professor_factory, course_factory):
    prof1 = professor_factory(first_name="Reza")
    prof2 = professor_factory(first_name="Nima")

    course_factory(name="Data Structures", professor=prof1)
    course_factory(name="Linear Algebra", professor=prof2)

    url = reverse("compare-professors") + "?search=Algebra"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["first_name"] == "Nima"


@pytest.mark.django_db
def test_professor_compare_empty_result(api_client):
    url = reverse("compare-professors") + "?search=NonexistentName"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_professor_compare_multiple_results(api_client, professor_factory):
    professor_factory(first_name="Ali")
    professor_factory(first_name="Ali")
    professor_factory(first_name="Sara")

    url = reverse("compare-professors") + "?search=Ali"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_professor_compare_professor_with_no_courses(api_client, professor_factory):
    professor = professor_factory(first_name="NoCourse")

    url = reverse("compare-professors") + "?search=NoCourse"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data[0]["courses"]) == 0
