# accounts/views.py
from datetime import timedelta

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

from .models import ActivationCode, User
from .serializers import ActivationCodeSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .throttles import PasswordResetThrottle
from .schema import activation_code_view_schema, password_reset_confirm_schema, password_reset_request_schema


@activation_code_view_schema
class ActivationCodeView(GenericAPIView):
    """
        Activate a user account via an activation code.
    """
    serializer_class = ActivationCodeSerializer

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


@password_reset_request_schema
class PasswordResetRequestView(GenericAPIView):
    """
        This view handles password reset requests by accepting a user's email address
        and sending a password reset link if the email is associated with an existing account.
    """
    serializer_class = [PasswordResetRequestSerializer]
    template_name = "emails/reset_password_email.html"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID

        reset_url = f"{settings.PASSWORD_RESET_URL}?token={token}&uid={uid}"

        subject = "رمز خود را تغییر دهید"
        from_email = settings.DEFAULT_FROM_EMAIL
        html_content = render_to_string(self.template_name, context={"username": user.username, "reset_url": reset_url})
        text_content = f""" سلام {user.username}
        برای تغییر رمز عبور خود وارد لینک زیر شوید. اگر برای تغییر رمز خود درخواستی نداده اید این ایمیل را نادیده بگیرید.
        {reset_url}
        """

        email_message = EmailMultiAlternatives(subject, text_content, from_email, [email])
        email_message.attach_alternative(html_content, "text/html")

        try:
            email_message.send(fail_silently=False)
        except Exception as e:
            # logger.error(f"Password reset email failed: {e}")
            pass

        return Response({"detail": "If this email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


@password_reset_confirm_schema
class PasswordResetConfirmView(GenericAPIView):
    """
        Handles confirmation of password reset by verifying UID, token, and new password.
    """
    serializer_class = [PasswordResetConfirmSerializer]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
