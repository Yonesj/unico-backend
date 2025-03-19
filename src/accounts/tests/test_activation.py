import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from src.accounts.models import ActivationCode


@pytest.mark.django_db
class TestActivationCodeView:
    endpoint = "/auth/activate-user/"

    def test_activate_user_success(self, api_client, user, activation_code):
        """
        Test that a valid activation code activates the user.
        """
        response = api_client.post(self.endpoint, {"activation_code": activation_code.code})
        user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "User activated successfully."
        assert user.is_active

    def test_activate_already_activated_user(self, api_client, user, activation_code):
        """
        Test that attempting to activate an already active user returns a 400 error.
        """
        user.is_active = True
        user.save()
        response = api_client.post(self.endpoint, {"activation_code": activation_code.code})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "User is already activated."

    def test_activate_invalid_code(self, api_client):
        """
        Test that an invalid activation code returns a 400 response with a generic message.
        """
        response = api_client.post(self.endpoint, {"activation_code": "INVLD12"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid activation code."

    def test_activate_expired_code(self, api_client, user, db):
        """
        Test that an expired activation code returns a 400 response.
        """
        expired_code = ActivationCode.objects.create(
            user=user,
            code="EXPRD12",
            created_at=timezone.now() - timedelta(minutes=11)  # expired: valid for 10 minutes
        )
        response = api_client.post(self.endpoint, {"activation_code": expired_code.code})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Activation code has expired."

    def test_throttling(self, api_client, settings):
        """
        Test that the throttle prevents too many activation attempts.
        """
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {'account_activation': '2/minute'}

        test_code = "INVLD12"  # valid-length code that does not exist.

        # Make two failed activation attempts.
        api_client.post(self.endpoint, {"activation_code": test_code})
        api_client.post(self.endpoint, {"activation_code": test_code})

        # The third attempt should now be throttled.
        response = api_client.post(self.endpoint, {"activation_code": test_code})
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
