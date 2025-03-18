from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class ActivationCodeThrottle(AnonRateThrottle):
    rate = '10/day'

class PasswordResetRequestThrottle(AnonRateThrottle):
    rate = "3/hour"

class PasswordResetConfirmThrottle(UserRateThrottle):
    rate = '3/hour'
