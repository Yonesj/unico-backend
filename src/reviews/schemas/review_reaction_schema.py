from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from src.utill.general_schemas import INVALID_AUTHENTICATION, TOO_MANY_REQUESTS, NOT_AUTHORIZED, BAD_REQUEST, NOT_FOUND
from src.reviews.serializers import ReviewReactionRetrieveSerializer, ReviewReactionCreateSerializer, ReviewReactionUpdateSerializer


my_review_reaction_list_schema = extend_schema(
    summary="List My Reactions to Professor's Reviews",
    description="Returns all reactions (like/dislike) the authenticated user has made on reviews for a given professor.",
    responses={
        200: OpenApiResponse(
            response=ReviewReactionRetrieveSerializer(many=True),
            description="A list of the user's review reactions for that professor.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value=[
                        {"id": 10, "review": 42, "value": 1},
                        {"id": 11, "review": 56, "value": -1},
                    ],
                    response_only=True
                )
            ]
        ),
        401: INVALID_AUTHENTICATION,
        403: NOT_AUTHORIZED,
        429: TOO_MANY_REQUESTS,
    }
)


review_reaction_create_schema = extend_schema(
    summary="React to a Review",
    description="Allows a verified UI student to like or dislike a specific review. Each user can react only once per review.",
    request=ReviewReactionCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="Reaction created successfully.",
            response=ReviewReactionRetrieveSerializer,
            examples=[
                OpenApiExample(
                    name="Success - Like",
                    value={"id": 123, "review": 42, "value": 1},
                    response_only=True
                ),
                OpenApiExample(
                    name="Success - Dislike",
                    value={"id": 124, "review": 42, "value": -1},
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


review_reaction_update_destroy_schema = extend_schema(
    summary="Update or Delete a Review Reaction",
    description="Allows the owner or an admin to update (PATCH) the value of a reaction or delete (DELETE) it entirely.",
    request=ReviewReactionUpdateSerializer,
    responses={
        200: OpenApiResponse(
            response=ReviewReactionRetrieveSerializer,
            description="Reaction updated successfully.",
            examples=[
                OpenApiExample(
                    name="Update to Like",
                    value={"id": 123, "review": 42, "value": 1},
                    response_only=True
                ),
                OpenApiExample(
                    name="Update to Dislike",
                    value={"id": 123, "review": 42, "value": -1},
                    response_only=True
                )
            ]
        ),
        204: OpenApiResponse(
            description="Reaction deleted successfully.",
            examples=[
                OpenApiExample(
                    name="Delete Response",
                    value="",
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        403: NOT_AUTHORIZED,
        404: NOT_FOUND,
        429: TOO_MANY_REQUESTS,
    }
)
