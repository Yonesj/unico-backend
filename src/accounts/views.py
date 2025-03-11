# accounts/views.py
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404


from .models import ActivationCode
from .serializers import ActivationCodeSerializer


class ActivationCodeView(APIView):
    """
    Endpoint to verify and activate a user account using only activation code.
    """

    def post(self, request):
        serializer = ActivationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['activation_code']

        activation_obj = get_object_or_404(ActivationCode, code=code)
        user = activation_obj.user

        if user.is_active:
            return Response({'detail': 'User is already activated.'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if not activation_obj.created_at or now > activation_obj.created_at + timedelta(minutes=10):
            return Response({'detail': 'Activation code has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save(update_fields=['is_active'])
        activation_obj.delete()

        return Response({'detail': 'User activated successfully.'}, status=status.HTTP_200_OK)
