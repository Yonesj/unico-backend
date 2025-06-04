from django.urls import path, include
from djoser.views import UserViewSet
from .views import ActivationCodeView, PasswordResetConfirmView, PasswordResetRequestView, ChangePasswordView


urlpatterns = [
    path('activate-user/', ActivationCodeView.as_view()),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('users/change_password/', ChangePasswordView.as_view(), name='user-change-password'),

    path('users/', UserViewSet.as_view(
        {
            'post': 'create'
        }
    ), name='user-create'),

    path('users/resend_activation/', UserViewSet.as_view(
        {'post': 'resend_activation'}
    ), name='resend-activation'),

    path('users/me/', UserViewSet.as_view(
        {
            'get': 'me',
            'put': 'me',
            'patch': 'me',
            'delete': 'me'
        }
    ), name='user-me'),

    path('', include('djoser.urls.jwt')),
]
