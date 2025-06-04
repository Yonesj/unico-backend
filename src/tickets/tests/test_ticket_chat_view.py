import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from src.tickets.models import Message
from src.tickets.models import Ticket


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
def auth_client(user_factory):
    user = user_factory(username="auth_user", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def ticket_factory(user_factory):
    counter = {'count': 0}

    def create_ticket(**kwargs):
        count = counter['count']
        counter['count'] += 1
        defaults = {
            'title': f'Test Ticket {count}',
            'user': user_factory(),
            'status': 'open',
        }
        defaults.update(kwargs)
        return Ticket.objects.create(**defaults)

    return create_ticket


@pytest.fixture
def ticket_message_factory(user_factory, ticket_factory):
    counter = {'count': 0}

    def create_message(**kwargs):
        count = counter['count']
        counter['count'] += 1
        defaults = {
            'ticket': ticket_factory(),
            'user': user_factory(),
            'body': f'Test message {count}',
        }
        defaults.update(kwargs)
        return Message.objects.create(**defaults)

    return create_message


@pytest.mark.django_db
def test_ticket_chat_owner_access(auth_client, ticket_factory, ticket_message_factory):
    client, user = auth_client
    ticket = ticket_factory(user=user)
    ticket_message_factory(ticket=ticket, user=user, body="First message")
    ticket_message_factory(ticket=ticket, user=user, body="Second message")

    url = reverse("retrieve-chat-panel", args=[ticket.id])
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["messages"][0]["body"] == "First message"
    assert response.data["messages"][1]["body"] == "Second message"


@pytest.mark.django_db
def test_ticket_chat_forbidden_for_other_user(api_client, user_factory, ticket_factory):
    owner = user_factory(username="owner", password="pass")
    intruder = user_factory(username="intruder", password="pass")

    ticket = ticket_factory(user=owner)
    url = reverse("retrieve-chat-panel", args=[ticket.id])

    client = api_client
    client.force_authenticate(user=intruder)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_ticket_chat_admin_access(api_client, user_factory, ticket_factory):
    owner = user_factory(username="owner", password="pass")
    admin = user_factory(username="admin", password="pass", is_staff=True)

    ticket = ticket_factory(user=owner)
    url = reverse("retrieve-chat-panel", args=[ticket.id])

    client = api_client
    client.force_authenticate(user=admin)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
