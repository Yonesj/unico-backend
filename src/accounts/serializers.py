from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as Base

from .models import User


class UserCreateSerializer(Base):
    """
        This serializer extends Djoser's `UserCreateSerializer` to define
        the required fields for creating a new user.

        **Fields**:
            - `id` (int): Auto-generated user ID.
            - `username` (str): Unique username for the user.
            - `email` (str): User's email address, used as the login identifier.
            - `password` (str): User's password (write-only).
    """

    class Meta(Base.Meta):
        fields = ['id', 'username', 'password', 'email']


class ActivationCodeSerializer(serializers.Serializer):
    """
       This serializer is used to validate the activation code provided by the user during the account activation process.

        **Fields**:
        - **activation_code** (str): A string field that accepts a maximum of 8 characters.
          This code is expected to be sent to the user and then provided back for validation.
    """
    activation_code = serializers.CharField(max_length=8)


class PasswordResetRequestSerializer(serializers.Serializer):
    """
        This serializer is used to validate the email address provided
        when a user requests a password reset.

        **Fields**:
            - `email` (str): The user's email address where the password reset link will be sent.
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
        This serializer is used to validate the data required for confirming
        a password reset, including the reset token and the new password.

        **Fields**:
            - `token` (str): A token generated for securely identifying the password reset request.
            - `password` (str): The new password to be set for the user (write-only).
            - `retyped_password` (str): Confirmation of the new password to ensure correctness (write-only).
    """
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    retyped_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        try:
            validate_password(value)
            return value
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

    def validate(self, attrs):
        token = attrs.get('token')
        password = attrs.get('password')
        retyped_password = attrs.get('retyped_password')

        if password != retyped_password:
            raise serializers.ValidationError("passwords must match")

        try:
            uid_b64 = self.context.get('uid_b64')
            uid = urlsafe_base64_decode(uid_b64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError({"token": "Invalid user."})

        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Token is expired or invalid."})

        self.context['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        password = self.validated_data['password']
        user.set_password(password)
        user.save()


class MessageSerializer(serializers.Serializer):
    """
        This serializer is used for generic message responses in API endpoints,
        such as success messages or error notifications.

        **Fields**:
            - `detail` (str): A message describing the result of the API request.
    """
    detail = serializers.CharField()
