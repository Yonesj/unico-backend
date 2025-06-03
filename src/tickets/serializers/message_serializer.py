from django.utils.translation import gettext as _
from rest_framework import serializers
import jdatetime
from rest_framework.exceptions import PermissionDenied

from src.tickets.models import Message, Ticket, TicketStatus


class MessageRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'user', 'body', 'date', 'time']

    def get_date(self, obj: Message) -> str:
        jalali_dt_obj = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
        return jalali_dt_obj.strftime("%Y/%m/%d")

    def get_time(self, obj: Message) -> str:
        local_time = obj.created_at.astimezone()
        return local_time.strftime("%H:%M")


class MessageCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Message
        fields = ['user', 'body']

    def validate(self, attrs):
        try:
            ticket = Ticket.objects.get(pk=self.context['ticket_pk'])
        except Ticket.DoesNotExist:
            raise serializers.ValidationError(_("Ticket does not exist"))

        request_user = attrs.get('user')
        is_ticket_owner = (ticket.user == request_user)
        is_admin_or_staff = (request_user.is_staff or request_user.is_superuser)

        if not (is_ticket_owner or is_admin_or_staff):
            raise PermissionDenied(_("You do not have permission to reply to this ticket."))

        if ticket.status == TicketStatus.CLOSED:
            raise serializers.ValidationError(
                {"ticket": _("Cannot add messages to a closed ticket.")}
            )

        attrs['ticket'] = ticket
        return attrs
