from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, NOT_AUTHORIZED, NOT_FOUND, TOO_MANY_REQUESTS

from src.tickets.serializers import MessageCreateSerializer, MessageRetrieveSerializer


message_create_schema = extend_schema(
    summary="Post a Message to a Ticket",
    description="""
        Adds a new message to an existing support ticket thread.
        Only the ticket owner or staff/admin may reply.
        Cannot add messages to a closed ticket.
    """,
    parameters=[
        OpenApiParameter(
            name="pk",
            description="Primary key of the ticket to which to post the message",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    request=MessageCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=MessageRetrieveSerializer,
            description="Message posted successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={
                        "id": 12,
                        "user": "alice",
                        "body": "Thanks, that worked!",
                        "date": "1404/03/05",
                        "time": "09:15"
                    },
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        403: NOT_AUTHORIZED,
        404: NOT_FOUND,
        429: TOO_MANY_REQUESTS,
    }
)
