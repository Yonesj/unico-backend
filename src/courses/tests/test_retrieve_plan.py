import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from src.courses.models.course import Course
from src.courses.models.plan import Plan
from django.core.cache import cache


@pytest.mark.django_db
class TestRetrievePlanView:

    @pytest.fixture
    def user(self, db, django_user_model):
        return django_user_model.objects.create_user(username='user1', password='pass1234', email='other@example.com')

    @pytest.fixture
    def other_user(self, db, django_user_model):
        return django_user_model.objects.create_user(username='user2', password='pass1234')

    @pytest.fixture
    def auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def course(self):
        return Course.objects.create(course_code='CS101', course_name='Test Course', theory='3', practical='0', capacity=30)

    @pytest.fixture
    def plan(self, user):
        return Plan.objects.create(name='Test Plan', user=user)

    def test_retrieve_own_plan(self, auth_client, plan):
        cache.clear()
        url = reverse('plan-detail', args=[plan.id])
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.data['id'] == plan.id
        assert response.data['name'] == plan.name

    def test_cannot_retrieve_others_plan(self, other_user, plan):
        cache.clear()
        client = APIClient()
        client.force_authenticate(user=other_user)

        url = reverse('plan-detail', args=[plan.id])
        response = client.get(url)

        assert response.status_code == 404
