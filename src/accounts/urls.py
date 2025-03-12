from django.urls import path
from .views import ActivationCodeView, PasswordResetConfirmView, PasswordResetRequestView


urlpatterns = [
    path('activate-user/', ActivationCodeView.as_view()),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
