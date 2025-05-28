from django.urls import path

from src.tickets.views import (
    TicketsListCreateView,
    TicketStatsView,
    TicketChatView
)

urlpatterns = [
    path('', TicketsListCreateView.as_view(), name='list-create-tickets'),
    path('stats/', TicketStatsView.as_view(), name='ticket-stats'),
    path('<int:pk>/messages/', TicketChatView.as_view(), name='create-message'),
    path('<int:pk>/', TicketChatView.as_view(), name='retrieve-chat-panel'),
]
