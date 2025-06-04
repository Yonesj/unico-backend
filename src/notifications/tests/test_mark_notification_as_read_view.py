import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from src.notifications.models import Notification


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
    def create(**kwargs):
        defaults = {
            'title': 'Test Notification',
            'body': 'Test Body',
            'type': 'info',
            'has_been_read': False,
        }
        defaults.update(kwargs)
        return Notification.objects.create(**defaults)

    return create


@pytest.mark.django_db
def test_mark_notification_as_read_success(auth_client, notification_factory):
    client, user = auth_client
    notif = notification_factory(user=user, has_been_read=False)

    url = reverse('mark-notification-as-read', args=[notif.id])
    response = client.patch(url)

    notif.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert notif.has_been_read is True


@pytest.mark.django_db
def test_mark_notification_as_read_by_other_user_forbidden(auth_client, user_factory, notification_factory):
    client, user = auth_client
    other_user = user_factory()
    notif = notification_factory(user=other_user, has_been_read=False)

    url = reverse('mark-notification-as-read', args=[notif.id])
    response = client.patch(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_mark_notification_as_read_not_found(auth_client):
    client, user = auth_client
    url = reverse('mark-notification-as-read', args=[999])
    response = client.patch(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_mark_notification_as_read_unauthenticated():
    client = APIClient()
    url = reverse('mark-notification-as-read', args=[1])
    response = client.patch(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
