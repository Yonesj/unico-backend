import pytest
from django.core import mail
from django.core.cache import cache
from rest_framework import status


@pytest.mark.django_db
class TestPasswordResetRequestView:
    endpoint = "/auth/password-reset/"

    def test_valid_password_reset_request(self, api_client, user):
        """
        Test that a valid password reset request sends an email.
        """
        cache.clear()
        response = api_client.post(self.endpoint, {"email": user.email})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "If this email exists, a reset link has been sent."
        assert len(mail.outbox) == 1  # Email should be sent
        assert user.email in mail.outbox[0].to  # Check email recipient

    def test_non_existent_email(self, api_client):
        """
        Test that requesting a password reset for a non-existent email does not reveal information.
        """
        cache.clear()
        response = api_client.post(self.endpoint, {"email": "doesnotexist@example.com"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "If this email exists, a reset link has been sent."
        assert len(mail.outbox) == 0  # No email should be sent

    def test_invalid_email_format(self, api_client):
        """
        Test that an invalid email format returns a 400 Bad Request.
        """
        cache.clear()
        response = api_client.post(self.endpoint, {"email": "invalid-email"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_throttling(self, api_client, settings, user):
        """
        Test that making too many password reset requests results in throttling.
        """
        cache.clear()
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {'password_reset': '2/minute'}

        # Send two valid requests (should be allowed)
        for _ in range(5):
            api_client.post(self.endpoint, {"email": user.email})

        # Third request should be throttled
        response = api_client.post(self.endpoint, {"email": user.email})
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
