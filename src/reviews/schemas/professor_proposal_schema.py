from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from src.reviews.serializers import ProfessorProposalCreateSerializer
from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS, INVALID_AUTHENTICATION, NOT_AUTHORIZED


professor_proposal_create_schema = extend_schema(
    summary="Submit Professor Proposal",
    description="Allows a verified UI student to propose a new professor record for approval.",
    request=ProfessorProposalCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=ProfessorProposalCreateSerializer,
            description="Proposal submitted successfully. It will be reviewed by an administrator.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={
                        "state": "pending",
                        "first_name": "Leila",
                        "last_name": "Hatami",
                        "faculty": 3,
                        "proposed_courses": ["Advanced English Grammar", "Poetry Analysis"],
                        "office_number": "B12",
                        "telegram_account": "@leila_h",
                        "email": "leila.h@example.com",
                        "website_url": "https://leila.example.com",
                        "office_location": "Building C, Room 204",
                        "profile_image": None,
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
