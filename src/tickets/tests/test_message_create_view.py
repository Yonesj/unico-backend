import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model


from src.tickets.models import Ticket, TicketStatus, Message

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
        return get_user_model().objects.create_user(**defaults)

    return create_user


@pytest.fixture
def ticket_factory(user_factory):
    def create_ticket(**kwargs):
        if 'user' not in kwargs:
            kwargs['user'] = user_factory(username='ticket_owner', password='pass1234')
        if 'status' not in kwargs:
            kwargs['status'] = TicketStatus.OPEN
        if 'title' not in kwargs:
            kwargs['title'] = 'Sample Ticket Title'
        return Ticket.objects.create(**kwargs)
    return create_ticket

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestMessageCreateView:

    @pytest.fixture(autouse=True)
    def setup(self, user_factory, ticket_factory):
        self.ticket_owner = user_factory(username='owner', password='pass1234')
        self.other_user = user_factory(username='other', password='pass1234')
        self.admin_user = user_factory(username='admin', password='pass1234', is_staff=True)
        self.ticket_open = ticket_factory(user=self.ticket_owner, status=TicketStatus.OPEN)
        self.ticket_closed = ticket_factory(user=self.ticket_owner, status=TicketStatus.CLOSED)

    def test_create_message_success_by_owner(self, api_client):
        api_client.force_authenticate(user=self.ticket_owner)
        url = reverse('create-message', kwargs={'pk': self.ticket_open.pk})
        data = {"body": "This is a test message from owner"}

        response = api_client.post(url, data)
        # assert response.status_code == status.HTTP_201_CREATED
        print(response.data)
        assert response.data['body'] == data['body']

        assert Message.objects.filter(ticket=self.ticket_open, user=self.ticket_owner, body=data['body']).exists()

    def test_create_message_success_by_admin(self, api_client):
        api_client.force_authenticate(user=self.admin_user)
        url = reverse('create-message', kwargs={'pk': self.ticket_open.pk})
        data = {"body": "Admin replying to ticket"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['body'] == data['body']

    def test_create_message_permission_denied_for_other_user(self, api_client):
        api_client.force_authenticate(user=self.other_user)
        url = reverse('create-message', kwargs={'pk': self.ticket_open.pk})
        data = {"body": "User who is not owner or admin"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "permission" in str(response.data).lower()

    def test_create_message_ticket_does_not_exist(self, api_client):
        api_client.force_authenticate(user=self.ticket_owner)
        url = reverse('create-message', kwargs={'pk': 99999})
        data = {"body": "Message to nonexistent ticket"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not exist" in str(response.data).lower()

    def test_create_message_closed_ticket(self, api_client):
        api_client.force_authenticate(user=self.ticket_owner)
        url = reverse('create-message', kwargs={'pk': self.ticket_closed.pk})
        data = {"body": "Trying to reply to closed ticket"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "closed ticket" in str(response.data).lower()

    def test_create_message_body_missing(self, api_client):
        api_client.force_authenticate(user=self.ticket_owner)
        url = reverse('create-message', kwargs={'pk': self.ticket_open.pk})
        data = {}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "body" in response.data

    def test_unauthenticated_cannot_create_message(self, api_client):
        url = reverse('create-message', kwargs={'pk': self.ticket_open.pk})
        data = {"body": "Anonymous message"}

        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
