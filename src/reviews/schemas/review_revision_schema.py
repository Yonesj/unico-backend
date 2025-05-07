from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, NOT_AUTHORIZED, TOO_MANY_REQUESTS
from src.reviews.serializers import ReviewRevisionCreateSerializer


review_revision_create_schema = extend_schema(
    summary="Submit a Review Edit",
    description="Allows the owner or an admin to submit an edit suggestion for a review. Only one pending revision per review is allowed.",
    request=ReviewRevisionCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="Review revision submitted successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"detail": "Review revision submitted successfully."},
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        403: NOT_AUTHORIZED,
        429: TOO_MANY_REQUESTS,
    }
)
