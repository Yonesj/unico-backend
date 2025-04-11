from djoser.serializers import UserCreateSerializer as Base


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
