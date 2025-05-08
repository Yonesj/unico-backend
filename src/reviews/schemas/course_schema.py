from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from src.reviews.serializers import CourseSummarySerializer
from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS


course_list_view_schema = extend_schema(
    summary="List Courses",
    description="Retrieve a list of courses. You may filter by `faculty_id` or search by course `name`.",
    parameters=[
        OpenApiParameter(
            name="faculty_id",
            description="Filter courses by the ID of their faculty.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="search",
            description="Search courses by name (partial, case-insensitive match).",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=CourseSummarySerializer(many=True),
            description="A list of matching courses.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {"id": 1, "name": "Introduction to Persian Literature"},
                        {"id": 2, "name": "Foundations of Theology"},
                        {"id": 3, "name": "Basics of Geology"}
                    ],
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)
