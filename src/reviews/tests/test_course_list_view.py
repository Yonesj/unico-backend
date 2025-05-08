import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from src.reviews.models import Course, Professor, Faculty


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def faculty():
    return Faculty.objects.create(name="Engineering")


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
def courses(faculty, professor):
    return [
        Course.objects.create(name="Algebra", professor=professor, faculty=faculty),
        Course.objects.create(name="Calculus", professor=professor, faculty=faculty),
        Course.objects.create(name="Physics", professor=professor, faculty=faculty),
    ]


@pytest.mark.django_db
def test_course_list_success(api_client, courses):
    url = reverse("list-course")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    returned_names = [course['name'] for course in response.data]
    for course in courses:
        assert course.name in returned_names


@pytest.mark.django_db
def test_course_list_filtered_by_faculty(api_client, faculty, professor):
    other_faculty = Faculty.objects.create(name="Science")
    Course.objects.create(name="Math", professor=professor, faculty=faculty)
    Course.objects.create(name="Biology", professor=professor, faculty=other_faculty)

    url = reverse("list-course")
    response = api_client.get(url, {'faculty_id': faculty.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Math"


@pytest.mark.django_db
def test_course_list_search(api_client, faculty, professor):
    Course.objects.create(name="Advanced Algebra", professor=professor, faculty=faculty)
    Course.objects.create(name="Intro to Programming", professor=professor, faculty=faculty)

    url = reverse("list-course")
    response = api_client.get(url, {'search': 'algebra'})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Advanced Algebra"


@pytest.mark.django_db
def test_course_list_empty(api_client):
    url = reverse("list-course")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
