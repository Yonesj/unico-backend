from djoser.serializers import UserCreateSerializer as Base


class UserCreateSerializer(Base):
    class Meta(Base.Meta):
        fields = ['id', 'username', 'password', 'email']
