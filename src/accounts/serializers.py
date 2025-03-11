from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as Base


class UserCreateSerializer(Base):
    class Meta(Base.Meta):
        fields = ['id', 'username', 'password', 'email']


class ActivationCodeSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=8)
