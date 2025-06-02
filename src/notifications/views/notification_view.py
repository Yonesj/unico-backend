from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from src.notifications.models import Notification
from src.notifications.serializers import NotificationRetrieveSerializer
from src.utill.permissions import IsOwnerOrAdmin


class NotificationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationRetrieveSerializer

    def get_queryset(self):
        return (
            Notification.objects
            .filter(user=self.request.user)
            .order_by('-created_at')[:20]
        )


class UnreadNotificationCountView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = request.user.notifications.filter(has_been_read=False).count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class MarkAllNotificationsAsReadView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        updated_count = Notification.objects.filter(
            user=request.user, has_been_read=False
        ).update(has_been_read=True)

        return Response({"updated": updated_count}, status=status.HTTP_200_OK)


class MarkAsReadView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Notification.objects.all()
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        notif = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])
        self.check_object_permissions(request, notif)

        notif.has_been_read = True
        notif.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
