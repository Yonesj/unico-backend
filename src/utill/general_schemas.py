from drf_spectacular.utils import OpenApiResponse, OpenApiExample


BAD_REQUEST = OpenApiResponse(
    description="Validation errors such as missing required fields",
    examples=[
        OpenApiExample(
            name="Validation Error",
            value={"field_name": ["This field is required."]},
            response_only=True,
        )
    ],
)

TOO_MANY_REQUESTS = OpenApiResponse(
    description="Too many requests. Please try again later.",
    examples=[
        OpenApiExample(
            name="Throttled",
            value={"detail": "Request was throttled. Please try again later."},
            response_only=True,
        )
    ],
)

INVALID_AUTHENTICATION = OpenApiResponse(
    description="Authentication credentials were not provided or are invalid.",
    examples=[
        OpenApiExample(
            name="Unauthorized",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
        )
    ],
)

NOT_AUTHORIZED = OpenApiResponse(
    description="Forbidden: The authenticated user does not have permission to modify this record.",
    examples=[
        OpenApiExample(
            name="Forbidden",
            value={"detail": "You do not have permission to perform this action."},
            response_only=True,
        )
    ],
)

NOT_FOUND = OpenApiResponse(
    description="Record not found or not accessable.",
    examples=[
        OpenApiExample(
            name="Not Found",
            value={"detail": "Not found."},
            response_only=True,
        )
    ],
)

INTERNAL_SERVER_ERROR = OpenApiResponse(
    description="Internal server error.",
    examples=[
        OpenApiExample(
            name="Internal Server Error",
            value={"detail": "internal server error"},
            response_only=True,
        )
    ],
)
