from uuid import uuid4
from rest_framework import serializers
from src.courses.models import Plan, Course
from .coures_serializer import CourseModelSerializer


class PlanRetrieveSerializer(serializers.ModelSerializer):
    courses = CourseModelSerializer(many=True, read_only=True)
    username = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ['id', 'username', 'share_uuid', 'courses']
        read_only_fields = ['id', 'username', 'share_uuid', 'courses']

    def get_username(self, obj):
        return obj.user.username if obj.user else None


class PlanCreateSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all()
    )

    class Meta:
        model = Plan
        fields = ['id', 'share_uuid', 'courses']
        read_only_fields = ['id', 'share_uuid']

    def create(self, validated_data):
        user = self.context['user']
        courses = validated_data.pop('courses', [])
        plan = Plan.objects.create(user=user, **validated_data)
        plan.courses.set(courses)
        return plan


class PlanUpdateSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all()
    )

    class Meta:
        model = Plan
        fields = ['id', 'courses']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        courses = validated_data.pop('courses', None)
        instance.save()
        if courses is not None:
            instance.courses.set(courses)
        return instance


class PlanRevokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'share_uuid']
        read_only_fields = ['id', 'share_uuid']

    def update(self, instance, validated_data):
        instance.share_uuid = uuid4()
        instance.save()
        return instance
