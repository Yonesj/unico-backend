from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, TOO_MANY_REQUESTS
from src.reviews.serializers import ReviewReportCreateSerializer


review_report_create_schema = extend_schema(
    summary="Report a Review",
    description="Allows an authenticated user to report a review. Each user can report a specific review only once.",
    request=ReviewReportCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="Report submitted successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"detail": "Report submitted successfully."},
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    }
)
