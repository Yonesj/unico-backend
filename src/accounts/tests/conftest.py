import pytest
from rest_framework.test import APIClient
from django.utils import timezone
from src.accounts.models import User, ActivationCode


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    """
    Create an inactive user for testing.
    """
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass",
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
