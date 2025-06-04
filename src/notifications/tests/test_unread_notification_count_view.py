import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse


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
def auth_client(user_factory):
    user = user_factory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def notification_factory():
    def create_notification(**kwargs):
        from src.notifications.models import Notification
        defaults = {
            'title': 'Test Notification',
            'body': 'This is a test notification.',
            'type': 'info',
            'has_been_read': False,
        }
        defaults.update(kwargs)
        return Notification.objects.create(**defaults)

    return create_notification


@pytest.mark.django_db
def test_unread_notification_count_returns_correct_count(auth_client, notification_factory):
    client, user = auth_client

    for _ in range(3):
        notification_factory(user=user, has_been_read=False)
    for _ in range(2):
        notification_factory(user=user, has_been_read=True)

    url = reverse('unread-notification-count')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_unread_notification_count_zero_when_all_read(auth_client, notification_factory):
    client, user = auth_client

    for _ in range(5):
        notification_factory(user=user, has_been_read=True)

    url = reverse('unread-notification-count')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0


@pytest.mark.django_db
def test_unread_notification_count_unauthenticated_user_cannot_access():
    client = APIClient()
    url = reverse('unread-notification-count')
    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
