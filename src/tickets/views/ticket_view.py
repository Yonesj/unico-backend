from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from src.tickets.models import Ticket, TicketStatus
from src.tickets.serializers import TicketListSerializer, TicketCreateSerializer, TicketChatSerializer
from src.utill.permissions import IsOwnerOrAdmin
from src.tickets.schemas import (
    tickets_list_create_schema_extension, ticket_chat_view_schema, ticket_stats_view_schema_extension
)


@tickets_list_create_schema_extension
class TicketsListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketCreateSerializer
        return TicketListSerializer

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)


@ticket_stats_view_schema_extension
class TicketStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        base_queryset = Ticket.objects.filter(user=request.user)

        stats = base_queryset.aggregate(
            open_count=Count('pk', filter=Q(status=TicketStatus.OPEN)),
            answered_count=Count('pk', filter=Q(status=TicketStatus.ANSWERED)),
            closed_count=Count('pk', filter=Q(status=TicketStatus.CLOSED)),
        )

        response_data = {
            'answered': stats.get('answered_count', 0),
            'closed': stats.get('closed_count', 0),
            'in_progress_or_open': stats.get('open_count', 0),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@ticket_chat_view_schema
class TicketChatView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = TicketChatSerializer
    queryset = Ticket.objects.prefetch_related('messages')
    lookup_field = 'pk'
