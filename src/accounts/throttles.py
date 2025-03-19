from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class ActivationCodeThrottle(AnonRateThrottle):
    scope = 'account_activation'


class PasswordResetRequestThrottle(AnonRateThrottle):
    scope = 'password_reset'


class PasswordResetConfirmThrottle(AnonRateThrottle):
    scope = 'password_reset'
