from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.tickets.models import Message
from src.tickets.serializers import MessageCreateSerializer


class MessageCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageCreateSerializer
    queryset = Message.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['ticket_pk'] = self.kwargs['pk']
        return ctx
