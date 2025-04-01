from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, extend_schema_view
from src.courses.serializers import PlanRetrieveSerializer, PlanCreateSerializer, PlanRevokeSerializer, PlanUpdateSerializer
from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS, NOT_AUTHORIZED, NOT_FOUND, INVALID_AUTHENTICATION


plan_list_create_view_schema = extend_schema_view(
    get=extend_schema(
        summary="List Plans",
        description="Retrieve a list of plans for the authenticated user.",
        responses={
            200: OpenApiResponse(
                response=PlanRetrieveSerializer,
                description="A list of plans for the authenticated user.",
                examples=[
                    OpenApiExample(
                        name="GET Response Example",
                        value=[
                            {
                                "id": 1,
                                "name": "My Plan",
                                "share_uuid": "550e8400-e29b-41d4-a716-446655440000",
                                "courses": [
                                    {
                                        "id": 12,
                                        "course_code": "10115_01",
                                        "course_name": "Computer Science 101",
                                        "theory": "3",
                                        "practical": "0",
                                        "capacity": 50,
                                        "gender": "M",
                                        "professor_name": "Prof. X",
                                        "class_location": "Room 101",
                                        "prerequisites": "None",
                                        "notes": ""
                                    }
                                ]
                            }
                        ],
                        response_only=True,
                    )
                ],
            ),
            400: BAD_REQUEST,
            401: INVALID_AUTHENTICATION,
            429: TOO_MANY_REQUESTS,
        },
    ),
    post=extend_schema(
        summary="Create Plan",
        description="Create a new plan for the authenticated user. The plan is created using the provided name and a list of course IDs.",
        request=PlanCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=PlanCreateSerializer,
                description="Plan created successfully.",
                examples=[
                    OpenApiExample(
                        name="POST Response Example",
                        value={
                            "id": 2,
                            "name": "New Plan",
                            "share_uuid": "123e4567-e89b-12d3-a456-426614174000",
                            "courses": [12, 34]
                        },
                        response_only=True,
                    )
                ],
            ),
            400: BAD_REQUEST,
            401: INVALID_AUTHENTICATION,
            429: TOO_MANY_REQUESTS,
        },
    )
)


plan_detail_view_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve Plan",
        operation_id="PlanDetailRetrieve",
        responses={
            200: OpenApiResponse(
                response=PlanRetrieveSerializer,
                description="Plan retrieved successfully.",
                examples=[
                    OpenApiExample(
                        name="GET Response Example",
                        value={
                            "id": 1,
                            "name": "My Plan",
                            "share_uuid": "550e8400-e29b-41d4-a716-446655440000",
                            "courses": [
                                {
                                    "id": 12,
                                    "course_code": "CS101",
                                    "course_name": "Computer Science 101",
                                    "theory": "3",
                                    "practical": "0",
                                    "capacity": 50,
                                    "gender": "M",
                                    "professor_name": "Prof. X",
                                    "class_location": "Room 101",
                                    "prerequisites": "None",
                                    "notes": ""
                                }
                            ]
                        },
                        response_only=True,
                    )
                ],
            ),
            400: BAD_REQUEST,
            401: INVALID_AUTHENTICATION,
            403: NOT_AUTHORIZED,
            404: NOT_FOUND,
            429: TOO_MANY_REQUESTS,
        },
    ),
    patch=extend_schema(
        summary="Update Plan",
        request=PlanUpdateSerializer,
        operation_id="PlanDetailUpdatePartial",
        responses={
            200: OpenApiResponse(
                response=PlanRetrieveSerializer,
                description="Plan updated successfully.",
                examples=[
                    OpenApiExample(
                        name="Update Response Example",
                        value={
                            "id": 1,
                            "name": "Updated Plan Name",
                            "share_uuid": "550e8400-e29b-41d4-a716-446655440000",
                            "courses": [
                                {
                                    "id": 12,
                                    "course_code": "CS101",
                                    "course_name": "Computer Science 101",
                                    "theory": "3",
                                    "practical": "0",
                                    "capacity": 50,
                                    "gender": "M",
                                    "professor_name": "Prof. X",
                                    "class_location": "Room 101",
                                    "prerequisites": "None",
                                    "notes": ""
                                }
                            ]
                        },
                        response_only=True,
                    )
                ],
            ),
            400: BAD_REQUEST,
            401: INVALID_AUTHENTICATION,
            403: NOT_AUTHORIZED,
            404: NOT_FOUND,
            429: TOO_MANY_REQUESTS,
        },
    ),
    delete=extend_schema(
        summary="Delete Plan",
        operation_id="PlanDetailDelete",
        responses={
            204: OpenApiResponse(
                description="Plan deleted successfully.",
                examples=[
                    OpenApiExample(
                        name="Delete Response",
                        value="",
                        response_only=True,
                    )
                ],
            ),
            400: BAD_REQUEST,
            401: INVALID_AUTHENTICATION,
            403: NOT_AUTHORIZED,
            404: NOT_FOUND,
            429: TOO_MANY_REQUESTS,
        },
    )
)


plan_retrieve_shared_view_description = """
This endpoint allows anyone with a valid shared link to retrieve a plan without authentication.

### 🔑 Expected Flow:
- A user clicks a shared link of the form:
  `https://domain.com/plans?share_uuid={uuid}`
- The endpoint looks up the plan by the provided **share_uuid**.
- On success, the plan details are returned, including its `id`, `name`, `share_uuid`, and nested course details.

### ⚙️ Security Considerations:
- The shared link uses a randomly generated **UUID** (via uuid4) to ensure the URL is unguessable.
- This endpoint is public and does not require authentication, so it should only expose non-sensitive plan data.

### ⚠️ Possible Responses:
- **200 OK:** Plan details are returned using the PlanRetrieveSerializer.
- **400 Bad Request:** The provided UUID is malformed.
- **404 Not Found:** No plan exists for the provided share_uuid.
- **429 Too Many Requests:** If rate limiting is applied.
"""

plan_retrieve_shared_view_schema = extend_schema(
    summary="Retrieve Shared Plan",
    operation_id="SharedPlanRetrieve",
    description=plan_retrieve_shared_view_description,
    responses={
        200: OpenApiResponse(
            response=PlanRetrieveSerializer,
            description="Plan retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Successful Response",
                    value={
                        "id": 1,
                        "name": "Shared Plan Example",
                        "share_uuid": "550e8400-e29b-41d4-a716-446655440000",
                        "courses": [
                            {
                                "id": 12,
                                "course_code": "CS101",
                                "course_name": "Computer Science 101",
                                "theory": "3",
                                "practical": "0",
                                "capacity": 50,
                                "gender": "M",
                                "professor_name": "Prof. X",
                                "class_location": "Room 101",
                                "prerequisites": "None",
                                "notes": ""
                            }
                        ]
                    },
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        404: NOT_FOUND,
        429: TOO_MANY_REQUESTS,
    },
)


plan_revoke_view_description = """
This endpoint allows the owner or an admin to revoke the current **share_uuid** of a plan and generate a new one.

### 🔑 Expected Flow:
1. The user (who must be the plan owner or an admin) sends a `PUT` or `PATCH` request.
2. The backend revokes the existing **share_uuid** and replaces it with a new one.
3. The new **share_uuid** is returned in the response.

### 🔒 Security Considerations:
- This action **requires authentication**.
- Only **the owner or an admin** can revoke a plan's shared UUID.
- The **new UUID is returned** so that the frontend can display or store the new share link.

### ⚠️ Possible Responses:
- **200 OK:** The UUID was successfully revoked and regenerated.
- **403 Forbidden:** The user is not authorized to perform this action.
- **404 Not Found:** The plan does not exist or is not owned by the user.
- **429 Too Many Requests:** If rate limiting is applied.
"""

plan_revoke_view_schema = extend_schema(
    summary="Revoke and Regenerate Plan Share UUID",
    operation_id="PlanRevokePut",
    description=plan_revoke_view_description,
    responses={
        200: OpenApiResponse(
            response=PlanRevokeSerializer,
            description="Share UUID successfully revoked and regenerated.",
            examples=[
                OpenApiExample(
                    name="Successful Revocation",
                    value={
                        "id": 1,
                        "name": "Updated Plan",
                        "share_uuid": "550e8400-e29b-41d4-a716-446655440000"
                    },
                    response_only=True,
                )
            ],
        ),
        403: NOT_AUTHORIZED,
        404: NOT_FOUND,
        429: TOO_MANY_REQUESTS,
    }
)
