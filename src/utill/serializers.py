from rest_framework import serializers


class GolestanRequestSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    password = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    """
        This serializer is used for generic message responses in API endpoints,
        such as success messages or error notifications.

        **Fields**:
            - `detail` (str): A message describing the result of the API request.
    """
    detail = serializers.CharField()
