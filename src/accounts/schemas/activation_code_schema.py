from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from src.utill.serializers import MessageSerializer
from src.accounts.serializers import ActivationCodeSerializer


activation_code_view_schema = extend_schema(
    summary="Activate User Account",
    description="Activate a user account using an activation code within 10 minutes of registration. "
                "This endpoint also enforces a rate limit to prevent abuse; exceeding the allowed number of "
                "requests results in a 429 (Too Many Requests) response.",
    request=ActivationCodeSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageSerializer,
            description="User activated successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"detail": "User activated successfully."},
                    response_only=True
                )
            ],
        ),
        400: OpenApiResponse(
            response=MessageSerializer,
            description="Activation failed due to an invalid activation code, an expired code, or the user is already activated.",
            examples=[
                OpenApiExample(
                    name="Already Activated",
                    value={"detail": "User is already activated."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Expired Code",
                    value={"detail": "Activation code has expired."},
                    response_only=True
                ),
                OpenApiExample(
                    name="Invalid Code",
                    value={"detail": "Invalid activation code."},
                    response_only=True
                )
            ],
        ),
        429: OpenApiResponse(
            response=MessageSerializer,
            description="Too many requests: The rate limit for activation attempts has been exceeded.",
            examples=[
                OpenApiExample(
                    name="Rate Limit Exceeded",
                    value={"detail": "Too many requests"},
                    response_only=True
                )
            ],
        ),
    },
    examples=[
        OpenApiExample(
            name="Valid Activation Code",
            value={"activation_code": "12345678"},
            description="A valid activation code that can be used to activate the account.",
            request_only=True,
        ),
        OpenApiExample(
            name="Invalid Activation Code",
            value={"detail": "Invalid activation code."},
            description="This response occurs when the activation code is invalid or does not exist.",
            response_only=True,
        ),
    ]
)
