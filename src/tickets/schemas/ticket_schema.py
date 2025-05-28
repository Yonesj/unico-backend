from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, NOT_AUTHORIZED, NOT_FOUND, TOO_MANY_REQUESTS
from src.tickets.models import TicketStatus
from src.tickets.serializers import TicketListSerializer, TicketCreateSerializer, TicketChatSerializer


tickets_list_create_schema_extension = extend_schema_view(
    # For GET (List) request
    list=extend_schema(
        summary="List User's Tickets",
        description="Retrieves a list of tickets created by the authenticated user. "
                    "Supports filtering by status and ordering by creation date.",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter tickets by status.',
                enum=[s[0] for s in TicketStatus.choices] # Dynamically get enum values
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Order tickets. Available fields: `created_at`. Prefix with `-` for descending.',
                enum=['created_at', '-created_at']
            ),
        ],
        responses={
            200: TicketListSerializer(many=True),
            401: INVALID_AUTHENTICATION,
            429: TOO_MANY_REQUESTS
        }
    ),
    # For POST (Create) request
    create=extend_schema(
        summary="Create a New Ticket",
        description="Creates a new ticket for the authenticated user. "
                    "A description is required, which will become the first message of the ticket.",
        request=TicketCreateSerializer, # References your TicketCreateSerializer
        responses={
            201: OpenApiResponse(
                response=TicketListSerializer, # Response body after successful creation, often the created object serialized for reading
                description="Ticket created successfully. Returns the created ticket details."
            ),
            400: OpenApiResponse(
                description="Bad Request - Validation Error",
                examples=[
                    OpenApiExample(
                        name='Validation Error Example (Unit Required)', # 'name' instead of 'summary' for OpenApiExample
                        summary='Unit required for technical subject',    # 'summary' is also fine for clarity
                        value={
                            "unit": ["For technical subjects, a specific unit must be selected."]
                        },
                        # response_only=False, # This is the default for request/response examples
                        # request_only=False
                    ),
                    OpenApiExample(
                        name='Validation Error Example (Missing Title)',
                        summary='Title is missing',
                        value={
                            "title": ["This field is required."]
                        }
                    )
                ]
            ),
            401: INVALID_AUTHENTICATION,
            429: TOO_MANY_REQUESTS
        }
    )
)


from rest_framework import serializers
class TicketStatsSerializer(serializers.Serializer):
    answered = serializers.IntegerField(help_text="Number of tickets with 'answered' status.")
    closed = serializers.IntegerField(help_text="Number of tickets with 'closed' status.")
    in_progress_or_open = serializers.IntegerField(help_text="Number of tickets with 'open' status.")

    class Meta:
        examples = {
            'application/json': {
                "answered": 5,
                "closed": 10,
                "in_progress_or_open": 2
            }
        }


ticket_stats_view_schema_extension = extend_schema(
    summary="Get Ticket Statistics",
    description="Retrieves statistics about the authenticated user's tickets, including counts for "
                "answered, closed, and open/in-progress tickets.",
    responses={
        200: OpenApiResponse(
            response=TicketStatsSerializer,
            description="Successfully retrieved ticket statistics.",
            examples=[
                OpenApiExample(
                    name="Successful Stats Response",
                    summary="Example of a successful statistics response.",
                    value={
                        "answered": 5,
                        "closed": 10,
                        "in_progress_or_open": 2
                    }
                )
            ]
        ),
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS
    }
)



ticket_chat_view_schema = extend_schema(
    summary="Retrieve a Support Ticket's Chat Thread",
    description="""
        Fetch a single support ticket by its primary key (`pk`) along with all of its messages in chronological order.
        Only the ticket's owner or an administrator may access this endpoint.
    """,
    parameters=[
        OpenApiParameter(
            name="pk",
            description="Primary key of the ticket to retrieve",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    request=None,
    responses={
        200: OpenApiResponse(
            response=TicketChatSerializer,
            description="Ticket details and full message thread",
            examples=[
                OpenApiExample(
                    name="Ticket Chat Example",
                    value={
                        "id": 1,
                        "uid": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Unable to login",
                        "status_display": "Open",
                        "messages": [
                            {
                                "id": 10,
                                "user": "alice",
                                "body": "I keep getting an auth error when logging in.",
                                "date": "1404/03/04",
                                "time": "12:34"
                            },
                            {
                                "id": 11,
                                "user": "support_agent",
                                "body": "Can you please confirm your username?",
                                "date": "1404/03/04",
                                "time": "12:45"
                            }
                        ]
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