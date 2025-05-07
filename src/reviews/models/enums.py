from django.db import models


class AttendancePolicy(models.TextChoices):
    MANDATORY_AND_AFFECTS = 'mandatory_affects', 'Attendance is important and directly affects grades'
    OPTIONAL_POSITIVE     = 'optional_positive', 'Attendance is not required but has a positive impact'
    NOT_TRACKED           = 'not_tracked', 'Attendance is not tracked'
    UNKNOWN               = 'unknown', "Don't remember"


class State(models.TextChoices):
    PENDING  = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
