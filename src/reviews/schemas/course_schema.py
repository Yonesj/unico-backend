from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter

from src.reviews.serializers import CourseSummarySerializer, CourseCreateSerializer
from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, TOO_MANY_REQUESTS


course_list_create_schema = extend_schema(
    summary="List and Create Courses",
    description="GET returns a list of courses (filterable by `faculty_id` and searchable by `name`).\n"
                "POST allows authenticated users to propose a new course for a professor; the course will be "
                "created in a pending state for admin validation.",
    parameters=[
        OpenApiParameter(
            name="faculty_id",
            description="Filter by faculty primary key.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="search",
            description="Search courses by name.",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    request=CourseCreateSerializer,
    responses={
        200: OpenApiResponse(
            description="A list of courses.",
            response=CourseSummarySerializer(many=True),
            examples=[
                OpenApiExample(
                    name="GET Response Example",
                    value=[
                        {"id": 1, "name": "Introduction to Persian Literature"},
                        {"id": 2, "name": "Foundations of Theology"}
                    ],
                    response_only=True
                )
            ]
        ),
        201: OpenApiResponse(
            description="Course created successfully (pending validation).",
            response=CourseCreateSerializer,
            examples=[
                OpenApiExample(
                    name="POST Response Example",
                    value={"id": 3, "professor": 5, "name": "Advanced Geology", "state": "pending"},
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    }
)
