from django.urls import path
from .views import (
    NotificationListView,
    UnreadNotificationCountView,
    MarkAllNotificationsAsReadView,
    MarkAsReadView
)

urlpatterns = [
    path('unread-count/', UnreadNotificationCountView.as_view(), name='unread-notification-count'),
    path('mark-all-as-read/', MarkAllNotificationsAsReadView.as_view(), name='mark-all-notifications-as-read'),
    path('<int:pk>/read/', MarkAsReadView.as_view(), name='mark-notification-as-read'),
    path('', NotificationListView.as_view(), name='list-notification'),
]
