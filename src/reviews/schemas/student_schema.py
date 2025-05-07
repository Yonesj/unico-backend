from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, TOO_MANY_REQUESTS
from src.utill.serializers import GolestanRequestSerializer


student_create_view_schema = extend_schema(
    summary="Create UI Student Profile",
    description="Authenticate against Golestan and create a student profile linked to the current user. "
                "Only available to authenticated users without an existing profile.",
    request=GolestanRequestSerializer,
    responses={
        201: OpenApiResponse(
            response=None,
            description="Profile created successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={"detail": "your profile were created successfully"},
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
        500: OpenApiResponse(
            description="An unexpected error occurred on the server.",
        ),
    }
)