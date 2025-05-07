from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from src.reviews.serializers import ProfessorRevisionCreateSerializer
from src.utill.general_schemas import BAD_REQUEST, INVALID_AUTHENTICATION, NOT_AUTHORIZED, TOO_MANY_REQUESTS


professor_revision_create_schema = extend_schema(
    summary="Submit Professor Revision",
    description="Allows a verified UI-student to propose edits to an existing professor record. "
                "Only one pending revision per professor per user is allowed.",
    request=ProfessorRevisionCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=ProfessorRevisionCreateSerializer,
            description="Revision submitted successfully. Pending admin approval.",
            examples=[
                OpenApiExample(
                    name="Success Example",
                    value={
                        "professor": 5,
                        "faculty": 2,
                        "proposed_courses": ["Advanced Algebra", "Topology"],
                        "office_number": "D34",
                        "telegram_account": "@student123",
                        "email": "student@example.com",
                        "website_url": "",
                        "office_location": "Building B, Room 12",
                        "profile_image": None,
                        "schedule_image": None,
                        "state": "pending",
                        "submitted_by": 42
                    },
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        403: NOT_AUTHORIZED,
        429: TOO_MANY_REQUESTS,
    }
)
