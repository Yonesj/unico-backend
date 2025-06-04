import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from src.tickets.models import Ticket, TicketStatus, TicketSubject, TicketUnit
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
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
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    u = user()
    api_client.force_authenticate(user=u)
    return api_client, u


@pytest.fixture
def ticket_factory():
    def create_ticket(**kwargs):
        defaults = {
            "title": "Sample Ticket",
            "subject": TicketSubject.FINANCIAL,
            "unit": TicketUnit.NONE,
            "status": TicketStatus.OPEN,
        }
        defaults.update(kwargs)
        return Ticket.objects.create(**defaults)
    return create_ticket


@pytest.mark.django_db
def test_ticket_stats_unauthenticated_user(client):
    url = reverse('ticket-stats')
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_ticket_stats_with_no_tickets(auth_client):
    client, _ = auth_client
    url = reverse('ticket-stats')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'answered': 0,
        'closed': 0,
        'in_progress_or_open': 0
    }


@pytest.mark.django_db
def test_ticket_stats_with_various_statuses(auth_client, ticket_factory):
    client, user = auth_client

    ticket_factory(user=user, status=TicketStatus.OPEN)
    ticket_factory(user=user, status=TicketStatus.OPEN)
    ticket_factory(user=user, status=TicketStatus.CLOSED)
    ticket_factory(user=user, status=TicketStatus.ANSWERED)
    ticket_factory(user=user, status=TicketStatus.CLOSED)

    other_user = get_user_model().objects.create_user(username='other', password='123')
    ticket_factory(user=other_user, status=TicketStatus.OPEN)

    url = reverse('ticket-stats')
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'answered': 1,
        'closed': 2,
        'in_progress_or_open': 2
    }
