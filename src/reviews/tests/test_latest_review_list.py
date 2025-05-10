import pytest
from django.urls import reverse
from rest_framework import status
from src.reviews.models import Review, ReviewRevision, State, Course, Professor, Faculty
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


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
def auth_client(api_client, user_factory):
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def url():
    return reverse('latest-reviews')


@pytest.mark.django_db
def test_successful_review_list_response(api_client, review_factory, url):
    review_factory()
    review_factory()
    review_factory()

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    for review in response.data['results']:
        assert 'id' in review
        assert 'review_text' in review
        assert 'professor' in review


@pytest.mark.django_db
def test_returns_maximum_4_reviews_due_to_pagination(api_client, review_factory, url):
    for _ in range(5):
        review_factory()

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 4


@pytest.mark.django_db
def test_reviews_are_ordered_by_created_at_desc(api_client, review_factory, url):
    review1 = review_factory()
    review2 = review_factory()
    review3 = review_factory()

    response = api_client.get(url)

    returned_ids = [item['id'] for item in response.data['results']]
    expected_ids = list(
        Review.objects.order_by('-created_at').values_list('id', flat=True)[:4]
    )

    assert returned_ids == expected_ids


@pytest.mark.django_db
def test_empty_review_list(api_client, url):
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'] == []


@pytest.mark.django_db
def test_view_is_publicly_accessible(api_client, review_factory, url):
    review_factory()
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_professor_field_structure(api_client, review_factory, url):
    review = review_factory()
    response = api_client.get(url)
    professor_data = response.data['results'][0]['professor']
    assert isinstance(professor_data, dict)
    assert 'first_name' in professor_data
    assert 'last_name' in professor_data
