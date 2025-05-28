from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework import serializers
import jdatetime

from src.tickets.models import Ticket, TicketSubject, TicketUnit, Message
from src.tickets.serializers import MessageRetrieveSerializer


class TicketListSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'uid',
            'title',
            'subject_display',
            'status_display',
            'date',
            'time',
        ]

    def get_date(self, obj: Ticket) -> str:
        jalali_dt_obj = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return jalali_dt_obj.strftime("%Y/%m/%d")

    def get_time(self, obj: Ticket) -> str:
        local_time = obj.created_at.astimezone()
        return obj.created_at.strftime("%H:%M")


class TicketCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    description = serializers.CharField(max_length=350, required=True,  write_only=True)

    class Meta:
        model = Ticket
        fields = [
            'user',
            'title',
            'subject',
            'unit',
            'description'
        ]

    def validate(self, attrs):
        subject = attrs.get('subject')
        unit = attrs.get('unit')

        if subject == TicketSubject.TECHNICAL and unit == TicketUnit.NONE:
            raise serializers.ValidationError(
                {"unit": _("For technical subjects, a specific unit must be selected.")}
            )

        if subject != TicketSubject.TECHNICAL:
            attrs['unit'] = TicketUnit.NONE

        return attrs

    def create(self, validated_data):
        description_content = validated_data.pop('description')

        with transaction.atomic():
            ticket_instance = Ticket.objects.create(**validated_data)

            Message.objects.create(
                ticket=ticket_instance,
                user=ticket_instance.user,
                body=description_content
            )

        return ticket_instance


class TicketChatSerializer(serializers.ModelSerializer):
    messages = MessageRetrieveSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'uid', 'title', 'status_display', 'messages']
        read_only_fields = fields
