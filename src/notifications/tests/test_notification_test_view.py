import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
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
def notification_factory(db, user_factory):
    def create_notification(**kwargs):
        defaults = {
            "user": kwargs.get("user") or user_factory(),
            "title": kwargs.get("title", "Test Notification"),
            "body": kwargs.get("body", "This is a test notification body."),
            "type": kwargs.get("type", "INFO"),
            "has_been_read": kwargs.get("has_been_read", False),
        }
        return Notification.objects.create(**defaults)

    return create_notification


@pytest.fixture
def auth_client(user_factory):
    user = user_factory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_notification_list_returns_only_authenticated_user_notifications(auth_client, notification_factory,
                                                                         user_factory):
    client, user = auth_client
    n1 = notification_factory(user=user, title="Notif 1")
    n2 = notification_factory(user=user, title="Notif 2")
    other_user = user_factory(username="otheruser")
    notification_factory(user=other_user, title="Other User Notif")

    url = reverse("list-notification")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    titles = [notif["title"] for notif in response.data]
    assert "Notif 1" in titles
    assert "Notif 2" in titles
    assert "Other User Notif" not in titles


@pytest.mark.django_db
def test_notification_list_ordering(auth_client, notification_factory):
    client, user = auth_client
    n1 = notification_factory(user=user, title="Older Notif")
    n2 = notification_factory(user=user, title="Newer Notif")

    url = reverse("list-notification")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["title"] == "Newer Notif"
    assert response.data[1]["title"] == "Older Notif"


@pytest.mark.django_db
def test_notification_list_limit_20(auth_client, notification_factory):
    client, user = auth_client
    for i in range(25):
        notification_factory(user=user, title=f"Notif {i}")

    url = reverse("list-notification")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 20


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access(client):
    url = reverse("list-notification")
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
