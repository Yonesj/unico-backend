import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from src.tickets.models import Ticket, Message, TicketSubject, TicketUnit, TicketStatus
from rest_framework.test import APIClient

User = get_user_model()


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
        return User.objects.create_user(**defaults)

    return create_user


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def create_ticket(user):
    def make_ticket(**kwargs):
        defaults = {
            "user": user,
            "title": "Test Ticket",
            "subject": TicketSubject.FINANCIAL,
            "unit": TicketUnit.NONE,
        }
        defaults.update(kwargs)
        return Ticket.objects.create(**defaults)

    return make_ticket


@pytest.mark.django_db
def test_list_tickets(auth_client, create_ticket):
    create_ticket(title="T1")
    create_ticket(title="T2", status=TicketStatus.ANSWERED)

    url = reverse("list-create-tickets")
    response = auth_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 2
    titles = [ticket["title"] for ticket in response.data]
    assert "T1" in titles and "T2" in titles


@pytest.mark.django_db
def test_filter_tickets_by_status(auth_client, create_ticket):
    create_ticket(title="Open Ticket", status=TicketStatus.OPEN)
    create_ticket(title="Closed Ticket", status=TicketStatus.CLOSED)

    url = reverse("list-create-tickets") + "?status=close"
    response = auth_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["status_display"] == TicketStatus.CLOSED.label


@pytest.mark.django_db
def test_ticket_create_success(auth_client):
    url = reverse("list-create-tickets")
    data = {
        "title": "New Ticket",
        "subject": TicketSubject.FINANCIAL,
        "unit": TicketUnit.NONE,
        "description": "This is a valid ticket.",
    }

    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    ticket = Ticket.objects.get(title="New Ticket")
    assert ticket.subject == TicketSubject.FINANCIAL
    assert Message.objects.filter(ticket=ticket, body="This is a valid ticket.").exists()


@pytest.mark.django_db
def test_ticket_create_validation_error_missing_unit(auth_client):
    url = reverse("list-create-tickets")
    data = {
        "title": "Tech Ticket",
        "subject": TicketSubject.TECHNICAL,
        "unit": TicketUnit.NONE,
        "description": "This needs a unit but unit is NONE.",
    }

    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "unit" in response.data


@pytest.mark.django_db
def test_ticket_create_for_non_technical_unit_is_forced_none(auth_client):
    url = reverse("list-create-tickets")
    data = {
        "title": "Non-Tech Ticket",
        "subject": TicketSubject.SUGGESTION,
        "unit": TicketUnit.NOTIFICATION,
        "description": "Should ignore unit.",
    }

    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    ticket = Ticket.objects.get(title="Non-Tech Ticket")
    assert ticket.unit == TicketUnit.NONE


@pytest.mark.django_db
def test_ticket_list_requires_authentication(client):
    url = reverse("list-create-tickets")
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_ticket_create_requires_authentication(client):
    url = reverse("list-create-tickets")
    response = client.post(url, {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_ticket_ordering_by_created_at(auth_client, create_ticket):
    t1 = create_ticket(title="Older Ticket")
    t2 = create_ticket(title="Newer Ticket")

    t1.created_at = t1.created_at.replace(year=2000)
    t1.save()

    url = reverse("list-create-tickets") + "?ordering=created_at"
    response = auth_client.get(url)

    assert response.status_code == 200
    assert response.data[0]["title"] == "Older Ticket"
