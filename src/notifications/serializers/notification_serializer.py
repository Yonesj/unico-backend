from rest_framework import serializers

from src.notifications.models import Notification


class NotificationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'has_been_read', 'type', 'created_at']
        read_only_fields = fields
