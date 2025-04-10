import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from src.courses.models.course import Course
from src.courses.models.plan import Plan
from django.core.cache import cache


@pytest.mark.django_db
class TestUpdatePlanView:

    @pytest.fixture
    def user(self, db, django_user_model):
        return django_user_model.objects.create_user(username='user1', password='pass1234', email='user@example.com')

    @pytest.fixture
    def other_user(self, db, django_user_model):
        return django_user_model.objects.create_user(username='user2', password='pass1234', email='other@example.com')

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
    def plan(self, user):
        return Plan.objects.create(user=user)

    def test_update_plan_name_and_courses(self, auth_client, plan, course):
        cache.clear()
        url = reverse('plan-detail', args=[plan.id])
        data = {
            "courses": [course.id]
        }

        response = auth_client.put(url, data, format='json')
        plan.refresh_from_db()

        assert response.status_code == 200
        assert list(plan.courses.all()) == [course]

    def test_update_plan_invalid_course(self, auth_client, plan):
        cache.clear()
        url = reverse('plan-detail', args=[plan.id])
        data = {
            "courses": [9999] 
        }
        response = auth_client.put(url, data, format='json')
        assert response.status_code == 400
        assert 'courses' in response.data

