import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from src.reviews.models import Review
from src.reviews.models import Professor
from src.reviews.models import Course, Faculty
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    counter = {'count': 0}

    def create_user(**kwargs):
        count = counter['count']
        counter['count'] += 1
        defaults = {
            'username': f'user_{count}',
            'email': f'user_{count}@example.com',
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        return get_user_model().objects.create_user(**defaults)

    return create_user


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
def course_factory(professor_factory):
    def create_course(**kwargs):
        if 'professor' not in kwargs:
            kwargs['professor'] = professor_factory()
        defaults = {'name': 'Test Course'}
        defaults.update(kwargs)
        return Course.objects.create(**defaults)

    return create_course


@pytest.fixture
def review_factory(course_factory, user_factory):
    def create_review(**kwargs):
        if 'course' not in kwargs:
            kwargs['course'] = course_factory()
        if 'user' not in kwargs:
            kwargs['user'] = user_factory()

        defaults = {
            'grading': 5,
            'exam_difficulty': 5,
            'general_knowledge': 5,
            'homework_difficulty': 5,
            'teaching_engagement': 5,
            'attendance_policy': 'not_tracked',
            'would_take_again': True,
            'review_text': 'Test review',
            'exam_resources': '',
            'received_score': 18.5,
            'state': 'approved',
        }
        defaults.update(kwargs)
        return Review.objects.create(**defaults)

    return create_review


@pytest.fixture
def url(self, professor_factory):
    professor = professor_factory()
    return reverse('retrieve-professor-reviews', kwargs={'pk': professor.pk})


@pytest.fixture
def professor_url(professor_factory):
    professor = professor_factory()
    return reverse('retrieve-professor-reviews', kwargs={'pk': professor.pk})


@pytest.mark.django_db
def test_successful_review_list(api_client, review_factory, professor_factory, course_factory):
    professor = professor_factory(id=61)
    course = course_factory(professor=professor)

    r1 = review_factory(course=course, state='approved')
    r2 = review_factory(course=course, state='approved')
    r1.save()
    r2.save()

    response = api_client.get(f'/professor-reviewer/professors/{professor.id}/reviews/', {'course_id': course.id})

    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 2
    for review in response.data['results']:
        assert 'id' in review
        assert 'course' in review
        assert 'grading' in review


@pytest.mark.django_db
def test_review_list_empty(api_client, professor_url):
    response = api_client.get(professor_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'] == []


@pytest.mark.django_db
def test_review_filter_by_course_id(api_client, review_factory, professor_url, course_factory):
    course1 = course_factory()
    course2 = course_factory()
    review_factory(course=course1)
    review_factory(course=course2)

    response = api_client.get(professor_url, {'course_id': course1.id})

    assert response.status_code == status.HTTP_200_OK
    assert all(r['course']['id'] == course1.id for r in response.data['results'])


@pytest.mark.django_db
def test_review_ordering_by_likes(api_client, review_factory, professor_factory, course_factory):
    professor = professor_factory(id=61)
    course = course_factory(professor=professor)
    r1 = review_factory(course=course, state='approved')
    r2 = review_factory(course=course, state='approved')
    r1.save()
    r2.save()
    response = api_client.get(f'/professor-reviewer/professors/{professor.id}/reviews/', {'course_id': course.id})
    reviews = Review.objects.filter(state='approved')
    ids = [r['id'] for r in response.data['results']]

    assert ids == [reviews[0].id, reviews[1].id]


@pytest.mark.django_db
def test_review_with_non_approved_state_not_included(api_client, review_factory, professor_url):
    review_factory(state='pending')
    review_factory(state='rejected')

    response = api_client.get(professor_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'] == []

@pytest.mark.django_db
def test_invalid_professor_id_returns_200(api_client):
    url = reverse('retrieve-professor-reviews', kwargs={'pk': 9999})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
