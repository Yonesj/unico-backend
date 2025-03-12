from rest_framework.throttling import UserRateThrottle


class PasswordResetThrottle(UserRateThrottle):
    rate = '3/hour'
