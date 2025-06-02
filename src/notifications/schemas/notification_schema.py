from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, TOO_MANY_REQUESTS, NOT_AUTHORIZED, NOT_FOUND

from src.notifications.serializers import NotificationRetrieveSerializer


notification_list_schema = extend_schema(
    summary="List Recent Notifications",
    description="Returns up to the 20 most recent notifications for the authenticated user, ordered by creation time.",
    responses={
        200: OpenApiResponse(
            response=NotificationRetrieveSerializer(many=True),
            description="A list of the user's most recent notifications.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {
                            "id": 45,
                            "title": "New Comment on Your Post",
                            "body": "Alice commented: “Great lecture today!”",
                            "has_been_read": False,
                            "type": "info",
                            "created_at": "2025-06-20T14:32:10Z"
                        },
                        {
                            "id": 44,
                            "title": "System Maintenance",
                            "body": "The site will be down tonight from 02:00–03:00.",
                            "has_been_read": True,
                            "type": "warning",
                            "created_at": "2025-06-19T09:15:07Z"
                        }
                    ],
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    },
)


unread_notification_count_schema = extend_schema(
    summary="Get Unread Notification Count",
    description="Returns the number of unread notifications for the authenticated user.",
    responses={
        200: OpenApiResponse(
            description="Unread notification count retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value={"count": 5},
                    response_only=True,
                )
            ],
        ),
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    },
)


mark_all_notifications_as_read_schema = extend_schema(
    summary="Mark All Notifications as Read",
    description="Marks all unread notifications for the authenticated user as read and returns the count of updated records.",
    responses={
        200: OpenApiResponse(
            description="Number of notifications marked as read.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"updated": 12},
                    response_only=True,
                )
            ],
        ),
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    },
)


mark_notification_as_read_schema = extend_schema(
    summary="Mark a Single Notification as Read",
    description="Marks the specified notification as read. Only the owner or an admin may perform this action.",
    responses={
        204: OpenApiResponse(
            description="Notification marked as read successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value=None,
                    response_only=True,
                )
            ],
        ),
        401: INVALID_AUTHENTICATION,
        403: NOT_AUTHORIZED,
        404: NOT_FOUND,
        429: TOO_MANY_REQUESTS,
    },
)
