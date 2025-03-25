import pytest
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.test import APIClient
from src.accounts.models import User, ActivationCode


@pytest.fixture
def api_client():
    client = APIClient()
    client.defaults['HTTP_ACCEPT_LANGUAGE'] = 'en'
    return client

@pytest.fixture
def user(db):
    """
    Create an inactive user for testing.
    """
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="OldPass123!",
        is_active=False
    )

@pytest.fixture
def activation_code(user, db):
    """
    Create a valid activation code for the given user.
    """
    return ActivationCode.objects.create(
        user=user,
        code="VALID123",
        created_at=timezone.now()
    )


@pytest.fixture
def valid_reset_data(user):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Return a dict of valid data with new valid password
    return {
        "uid": uid,
        "token": token,
        "password": "NewStrongPass123!",
        "retyped_password": "NewStrongPass123!"
    }

