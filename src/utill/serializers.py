from rest_framework import serializers


class GolestanRequestSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    password = serializers.CharField()
