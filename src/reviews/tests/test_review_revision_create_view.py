import pytest
from rest_framework import status
from django.urls import reverse
from src.reviews.models import Review, ReviewRevision, State, Course, Professor, Faculty
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


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
def course_factory(professor_factory):
    def create_course(**kwargs):
        if 'professor' not in kwargs:
            kwargs['professor'] = professor_factory()
        defaults = {'name': 'Test Course'}
        defaults.update(kwargs)
        return Course.objects.create(**defaults)
    return create_course


@pytest.fixture
def review_revision_factory(review_factory):
    def create_review_revision(**kwargs):
        review = kwargs.get('review', review_factory())
        return ReviewRevision.objects.create(
            review=review,
            state=kwargs.get('state', State.PENDING),
            grading=kwargs.get('grading', 5),
            exam_difficulty=kwargs.get('exam_difficulty', 5),
            general_knowledge=kwargs.get('general_knowledge', 5),
            homework_difficulty=kwargs.get('homework_difficulty', 5),
            teaching_engagement=kwargs.get('teaching_engagement', 5),
            exam_resources=kwargs.get('exam_resources', "Resources for exam"),
            attendance_policy=kwargs.get('attendance_policy', "not_tracked"),
            would_take_again=kwargs.get('would_take_again', True),
            received_score=kwargs.get('received_score', 18.5),
            review_text=kwargs.get('review_text', "Test review text")
        )
    return create_review_revision

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
def faculty(db):
    return Faculty.objects.create(name="Engineering")


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
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def review_revision_create_url():
    def _make_url(review_id):
        return f'/professor-reviewer/reviews/{review_id}/revisions/'
    return _make_url

@pytest.mark.django_db
def test_create_review_revision_success(auth_client, review_factory, review_revision_create_url):
    review = review_factory()
    url = review_revision_create_url(review.id)

    data = {
        'grading': 4,
        'exam_difficulty': 3,
        'general_knowledge': 3,
        'homework_difficulty': 4,
        'teaching_engagement': 3,
        'attendance_policy': 'not_tracked',
        'would_take_again': False,
        'received_score': 18.0,
        'review_text': 'Great course, but needs improvement in teaching',
    }

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['grading'] == data['grading']
    assert response.data['review_text'] == data['review_text']


@pytest.mark.django_db
def test_create_review_revision_duplicate_pending(auth_client, review_revision_factory, review_revision_create_url):
    revision = review_revision_factory(state=State.PENDING)
    review = revision.review
    url = review_revision_create_url(review.id)

    data = {
        'grading': 4,
        'exam_difficulty': 3,
        'general_knowledge': 3,
        'homework_difficulty': 4,
        'teaching_engagement': 3,
        'attendance_policy': 'not_tracked',
        'would_take_again': False,
        'received_score': 18.0,
        'review_text': 'Great course, but needs improvement in teaching',
    }

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'review' in response.data
    assert response.data['review'][0] == 'There is already a pending edit for this review'


@pytest.mark.django_db
def test_create_review_revision_permission_error(api_client, review_factory, review_revision_create_url):
    review = review_factory(user=None)
    url = review_revision_create_url(review.id)

    data = {
        'grading': 4,
        'exam_difficulty': 3,
        'general_knowledge': 3,
        'homework_difficulty': 4,
        'teaching_engagement': 3,
        'attendance_policy': 'not_tracked',
        'would_take_again': False,
        'received_score': 18.0,
        'review_text': 'Great course, but needs improvement in teaching',
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data


@pytest.mark.django_db
def test_create_review_revision_invalid_data(auth_client, review_factory, review_revision_create_url):
    review = review_factory(user=None)
    url = review_revision_create_url(review.id)

    data = {
        'grading': None,
        'exam_difficulty': None,
        'general_knowledge': None,
        'homework_difficulty': None,
        'teaching_engagement': None,
        'attendance_policy': 'not_tracked',
        'would_take_again': None,
        'received_score': 25.0,
        'review_text': '',
    }

    response = auth_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST



@pytest.mark.django_db
def test_create_review_revision_unauthenticated(api_client, review_factory, review_revision_create_url):
    review = review_factory()
    url = review_revision_create_url(review.id)
    data = {
        'grading': 5,
        'exam_difficulty': 5,
        'general_knowledge': 5,
        'homework_difficulty': 5,
        'teaching_engagement': 5,
        'attendance_policy': 'not_tracked',
        'would_take_again': True,
        'received_score': 15.0,
        'review_text': 'Excellent course with clear explanations.',
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_review_revision_invalid_review_id(auth_client, review_revision_create_url):
    url = review_revision_create_url(999999)
    data = {
        'grading': 5,
        'exam_difficulty': 5,
        'general_knowledge': 5,
        'homework_difficulty': 5,
        'teaching_engagement': 5,
        'attendance_policy': 'not_tracked',
        'would_take_again': True,
        'received_score': 18.0,
        'review_text': 'Excellent course!',
    }

    response = auth_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND
