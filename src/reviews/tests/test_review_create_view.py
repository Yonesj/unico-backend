import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from src.reviews.models import Review, Professor, Course, State

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def professor_factory():
    def create_professor(**kwargs):
        defaults = {'first_name': 'Ali', 'last_name': 'Ahmadi'}
        defaults.update(kwargs)
        return Professor.objects.create(**defaults)

    return create_professor


@pytest.fixture
def course_factory(professor_factory):
    def create_course(**kwargs):
        if 'professor' not in kwargs:
            kwargs['professor'] = professor_factory()
        defaults = {'name': 'Test Course', 'state' : 'approved'}
        defaults.update(kwargs)
        return Course.objects.create(**defaults)

    return create_course


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
def ui_student(user_factory):
    return user_factory(is_ui_student=True)


@pytest.fixture
def student_user(user_factory):
    return user_factory(is_ui_student=True)


@pytest.fixture
def user_no_student(user_factory):
    return user_factory(is_ui_student=False)


@pytest.fixture
def auth_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def no_auth_client(api_client, user_no_student):
    api_client.force_authenticate(user=user_no_student)
    return api_client


@pytest.fixture
def auth_ui_student_client(student_user):
    client = APIClient()
    client.force_authenticate(user=student_user)
    return client


@pytest.fixture
def review_payload(course):
    return {
        "course": course.id,
        "grading": 4,
        "exam_difficulty": 3,
        "general_knowledge": 5,
        "homework_difficulty": 2,
        "teaching_engagement": 4,
        "exam_resources": "Textbook, Slides",
        "attendance_policy": "mandatory_affects",
        "would_take_again": True,
        "received_score": 18.5,
        "review_text": "Great course, very engaging."
    }


@pytest.fixture
def course(course_factory):
    return course_factory()


@pytest.mark.django_db
def test_successful_review_creation(auth_ui_student_client, student_user, review_payload, course):
    url = reverse('create-review')
    current_course_id_in_payload = review_payload['course']
    assert current_course_id_in_payload == course.id, "Mismatch between course in payload and course fixture"
    response = auth_ui_student_client.post(url, data=review_payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_duplicate_review_rejected(auth_ui_student_client, student_user, course, review_payload):
    assert review_payload[
               'course'] == course.id, "Mismatch between course in payload and course fixture for pre-creation"
    Review.objects.create(user=student_user, course=course, grading=3, exam_difficulty=3,
                          general_knowledge=3, homework_difficulty=3, teaching_engagement=3,
                          exam_resources="", attendance_policy="mandatory_affects", would_take_again=True)
    url = reverse('create-review')
    response = auth_ui_student_client.post(url, data=review_payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "You have already submitted a review for this course" in str(response.data)


@pytest.mark.django_db
def test_validation_error_missing_fields(auth_ui_student_client, course):
    url = reverse('create-review')
    payload = {"course": course.id, "would_take_again": True, }
    response = auth_ui_student_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'grading' in response.data
    assert 'exam_difficulty' in response.data


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_review(api_client, review_payload):
    url = reverse('create-review')
    response = api_client.post(url, data=review_payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_without_permission_cannot_create_review(no_auth_client, review_payload):
    url = reverse('create-review')
    response = no_auth_client.post(url, data=review_payload, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
