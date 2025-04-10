import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from src.courses.models.plan import Plan
from uuid import UUID
from django.core.cache import cache


@pytest.mark.django_db
class TestPlanRevokeView:

    @pytest.fixture
    def user(self, db, django_user_model):
        return django_user_model.objects.create_user(id=1, username='user1', password='pass1234', email='other@example.com')

    @pytest.fixture
    def admin_user(self, django_user_model):
        return django_user_model.objects.create_superuser(id=2, username='admin', password='adminpass')

    @pytest.fixture
    def other_user(self, django_user_model):
        return django_user_model.objects.create_user(id=3, username='other', password='pass1234', email="other2@gmail.com")

    @pytest.fixture
    def client(self):
        client = APIClient()
        client.defaults['HTTP_ACCEPT_LANGUAGE'] = 'en'
        return client

    @pytest.fixture
    def plan(self, user):
        return Plan.objects.create(user=user)

    def test_successful_revoke_by_owner(self, client, user, plan):
        cache.clear()
        client.force_authenticate(user=user)
        url = reverse('plan-link-rovoke', kwargs={'pk': plan.id})
        original_uuid = plan.share_uuid
        response = client.patch(url)

        assert response.status_code == status.HTTP_200_OK
        plan.refresh_from_db()
        assert response.data['id'] == plan.id
        assert UUID(response.data['share_uuid'])
        assert plan.share_uuid != original_uuid

    def test_successful_revoke_by_admin(self, client, admin_user, plan):
        cache.clear()
        client.force_authenticate(user=admin_user)
        url = reverse('plan-link-rovoke', kwargs={'pk': plan.id})
        response = client.patch(url)

        assert response.status_code == status.HTTP_200_OK
        plan.refresh_from_db()
        assert UUID(response.data['share_uuid'])

    def test_permission_denied_for_non_owner(self, client, other_user, plan):
        cache.clear()
        client.force_authenticate(user=other_user)
        url = reverse('plan-link-rovoke', kwargs={'pk': plan.id})
        response = client.patch(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user(self, client, plan):
        cache.clear()
        url = reverse('plan-link-rovoke', kwargs={'pk': plan.id})
        response = client.patch(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_plan_does_not_exist(self, client, user):
        cache.clear()
        client.force_authenticate(user=user)
        url = reverse('plan-link-rovoke', kwargs={'pk': 9999})
        response = client.patch(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
