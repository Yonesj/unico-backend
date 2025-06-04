from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from src.accounts.models import User
from src.accounts.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer
from src.accounts.throttles import PasswordResetConfirmThrottle, PasswordResetRequestThrottle
from src.accounts.schemas import password_reset_request_schema, password_reset_confirm_schema


@password_reset_request_schema
class PasswordResetRequestView(GenericAPIView):
    """
        This view handles password reset requests by accepting a user's email address
        and sending a password reset link if the email is associated with an existing account.
    """
    serializer_class = [PasswordResetRequestSerializer]
    throttle_classes = [PasswordResetRequestThrottle]
    template_name = "emails/reset_password_email.html"

    def post(self, request):
        throttle = PasswordResetRequestThrottle()
        if not throttle.allow_request(request, self):
            return Response({"detail": _("Too many requests")}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": _("If this email exists, a reset link has been sent.")}, status=status.HTTP_200_OK)

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

        return Response({"detail": _("If this email exists, a reset link has been sent.")}, status=status.HTTP_200_OK)


@password_reset_confirm_schema
class PasswordResetConfirmView(GenericAPIView):
    """
        Handles confirmation of password reset by verifying UID, token, and new password.
    """
    serializer_class = [PasswordResetConfirmSerializer]
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request):
        throttle = PasswordResetConfirmThrottle()
        if not throttle.allow_request(request, self):
            return Response({"detail": _("Too many requests")}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('Password has been reset successfully.')}, status=status.HTTP_200_OK)


class ChangePasswordView(GenericAPIView):
    """
    Authenticated users can POST here to change their password without needing
    to supply the old password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password has been changed successfully."},
            status=status.HTTP_200_OK
        )
