import pytest
import uuid
from django.urls import reverse
from rest_framework.test import APIClient
from src.courses.models.course import Course
from src.courses.models.plan import Plan
from django.core.cache import cache


@pytest.mark.django_db
class TestRetrieveSharedPlanView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self, db, django_user_model):
        return django_user_model.objects.create_user(id=1, username='user1', password='pass1234', email='other@example.com')

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
    def plan_with_course(self, course, user):
        plan = Plan.objects.create(name='Shared Plan', user=user)
        plan.courses.add(course)
        return plan

    @pytest.fixture
    def plan_without_courses(self, user):
        return Plan.objects.create(name='Empty Plan', user=user)

    def test_retrieve_shared_plan_success(self, api_client, plan_with_course):
        cache.clear()
        url = reverse('retrieve-shared-plan', kwargs={'share_uuid': plan_with_course.share_uuid})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['id'] == plan_with_course.id
        assert response.data['name'] == plan_with_course.name
        assert isinstance(response.data['courses'], list)
        assert len(response.data['courses']) == 1

    def test_retrieve_plan_invalid_uuid(self, api_client):
        cache.clear()
        url = '/course-scheduler/plans/not-a-valid-uuid/'
        response = api_client.get(url)
        assert response.status_code == 404

    def test_retrieve_plan_not_found(self, api_client):
        cache.clear()
        random_uuid = uuid.uuid4()
        url = reverse('retrieve-shared-plan', kwargs={'share_uuid': random_uuid})
        response = api_client.get(url)

        assert response.status_code == 404

    def test_retrieve_shared_plan_with_no_courses(self, api_client, plan_without_courses):
        cache.clear()
        url = reverse('retrieve-shared-plan', kwargs={'share_uuid': plan_without_courses.share_uuid})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data['id'] == plan_without_courses.id
        assert response.data['courses'] == []

    def test_head_request_on_shared_plan(self, api_client, plan_with_course):
        cache.clear()
        url = reverse('retrieve-shared-plan', kwargs={'share_uuid': plan_with_course.share_uuid})
        response = api_client.head(url)

        assert response.status_code == 200
        assert response.content == b''
