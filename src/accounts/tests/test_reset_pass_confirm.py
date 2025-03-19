import pytest
from rest_framework import status
from django.core.cache import cache


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    endpoint = "/auth/password-reset/confirm/"

    def test_valid_password_reset(self, api_client, user, valid_reset_data):
        """Test that a valid password reset request resets the user's password."""
        cache.clear()
        response = api_client.post(self.endpoint, valid_reset_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Password has been reset successfully."
        user.refresh_from_db()
        assert user.check_password(valid_reset_data["password"])

    def test_invalid_uid(self, api_client, user, valid_reset_data):
        """Test that an invalid UID returns an error."""
        cache.clear()
        invalid_data = valid_reset_data.copy()
        invalid_data["uid"] = "invalidUID"
        response = api_client.post(self.endpoint, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "uid" in response.data

    def test_invalid_token(self, api_client, user, valid_reset_data):
        """Test that an invalid token returns an error."""
        cache.clear()
        invalid_data = valid_reset_data.copy()
        invalid_data["token"] = "invalid-token"
        response = api_client.post(self.endpoint, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "token" in response.data

    def test_passwords_do_not_match(self, api_client, user, valid_reset_data):
        """Test that non-matching passwords return an error."""
        cache.clear()
        invalid_data = valid_reset_data.copy()
        invalid_data["retyped_password"] = "DifferentPass123!"
        response = api_client.post(self.endpoint, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # response.data["retyped_password"] is a list of error messages
        assert any("Passwords do not match" in err for err in response.data.get("retyped_password", []))

    def test_invalid_new_password(self, api_client, user, valid_reset_data):
        """Test that a new password failing validation returns an error."""
        cache.clear()
        invalid_data = valid_reset_data.copy()
        # Assuming the password validator rejects short passwords; use an obviously weak password.
        invalid_data["password"] = "123"
        invalid_data["retyped_password"] = "123"
        response = api_client.post(self.endpoint, invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_throttling(self, api_client, user, valid_reset_data, settings):
        """
        Test that too many password reset confirmations result in throttling.
        For testing, override the throttle rate for this view to a low value.
        """
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"password_reset": "2/minute"}
        cache.clear()  # Ensure throttle counter starts from zero

        # Use invalid token data to quickly trigger throttling.
        invalid_data = valid_reset_data.copy()
        invalid_data["token"] = "invalid-token"

        # Send two requests that will fail (but count towards throttle).
        for _ in range(5):
            api_client.post(self.endpoint, invalid_data)
        # Third request should be throttled.
        response = api_client.post(self.endpoint, valid_reset_data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
