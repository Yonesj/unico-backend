from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from src.reviews.serializers import FacultyRetrieveSerializer
from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS


faculty_list_view_schema = extend_schema(
    summary="List Faculties",
    description="Retrieve a list of all faculties. Supports optional `search` query parameter to filter by faculty name.",
    parameters=[
        OpenApiParameter(
            name='search',
            description='Search term to filter faculties by name',
            required=False,
            type=str,
            location=OpenApiParameter.QUERY
        )
    ],
    responses={
        200: OpenApiResponse(
            response=FacultyRetrieveSerializer(many=True),
            description="A list of faculties matching the optional search term.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {"id": 1, "name": "Engineering"},
                        {"id": 2, "name": "Arts & Humanities"},
                        {"id": 3, "name": "Sciences"}
                    ],
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)
