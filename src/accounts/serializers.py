from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as Base

from .models import User

class UserCreateSerializer(Base):
    class Meta(Base.Meta):
        fields = ['id', 'username', 'password', 'email']


class ActivationCodeSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=8)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
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
