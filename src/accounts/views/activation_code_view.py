from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from src.accounts.models import ActivationCode
from src.accounts.serializers import ActivationCodeSerializer
from src.accounts.throttles import ActivationCodeThrottle
from src.accounts.schemas import activation_code_view_schema


@activation_code_view_schema
class ActivationCodeView(GenericAPIView):
    """
        Activate a user account via an activation code.
    """
    serializer_class = ActivationCodeSerializer
    throttle_classes = [ActivationCodeThrottle]

    def post(self, request):
        throttle = ActivationCodeThrottle()
        if not throttle.allow_request(request, self):
            return Response({"detail": _("Too many requests")}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = ActivationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['activation_code']

        try:
            activation_obj = ActivationCode.objects.select_related('user').get(code=code)
        except ActivationCode.DoesNotExist:
            return Response({'detail': _('Invalid activation code.')}, status=status.HTTP_400_BAD_REQUEST)

        user = activation_obj.user

        if user.is_active:
            return Response({'detail': _('User is already activated.')}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if not activation_obj.created_at or now > activation_obj.created_at + timedelta(minutes=10):
            return Response({'detail': _('Activation code has expired.')}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save(update_fields=['is_active'])
        activation_obj.delete()

        return Response({'detail': _('User activated successfully.')}, status=status.HTTP_200_OK)
