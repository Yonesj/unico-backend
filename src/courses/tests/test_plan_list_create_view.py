import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import cache
from src.accounts.models import User
from src.courses.models.course import Course
from src.courses.models.plan import Plan


@pytest.mark.django_db
class TestPlanListCreateView:

    @pytest.fixture
    def user(self, db, django_user_model):
        return django_user_model.objects.create_user(id=1, username='user1', password='pass1234',
                                                     email='other@example.com')

    @pytest.fixture
    def auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_ACCEPT_LANGUAGE'] = 'en'
        return client

    @pytest.fixture
    def course(self):
        return Course.objects.create(
            id=1,
            course_code="1",
            course_name="Course 1",
            theory="1",
            practical="1",
            capacity=30,
            professor_name="Dr. Smith"
        )

    @pytest.fixture
    def url(self):
        return reverse('retrieve-create-plans')

    def test_get_empty_list(self, auth_client, url):
        cache.clear()
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_create_plan_successfully(self, auth_client, url, course):
        cache.clear()
        data = {
            "courses": [course.id]
        }
        response = auth_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Plan.objects.count() == 1
        plan = Plan.objects.first()
        assert course in plan.courses.all()

    def test_get_user_plans_only(self, auth_client, user, url):
        cache.clear()
        other_user = User.objects.create_user(
            username='other',
            password='pass1234',
            email='other2@example.com'
        )
        other_plan = Plan.objects.create(user=other_user)
        my_plan = Plan.objects.create(user=user)

        response = auth_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == my_plan.id

    def test_create_plan_with_invalid_course(self, auth_client, url):
        cache.clear()
        data = {
            "courses": [9999]
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'courses' in response.data

    def test_unauthenticated_user_cannot_access(self, client, url):
        cache.clear()
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.post(url, {"courses": []})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_plan_with_empty_course_list(self, auth_client, url):
        cache.clear()
        data = {
            "courses": []
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
