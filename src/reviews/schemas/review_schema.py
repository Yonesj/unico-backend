from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS, NOT_FOUND, INVALID_AUTHENTICATION, NOT_AUTHORIZED
from src.reviews.serializers import (
    ReviewCardSerializer, ReviewRetrieveSerializer, MyReviewRetrieveSerializer, ReviewCreateSerializer
)


latest_review_list_schema = extend_schema(
    summary="List Latest Reviews",
    description="Retrieve the most recent reviews across all professors, paginated with `limit` and `offset` parameters.",
    parameters=[
        OpenApiParameter(
            name="limit",
            description="Maximum number of reviews to return (default 4, max 10).",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="offset",
            description="Offset into the review list.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ReviewCardSerializer(many=True),
            description="A paginated list of the latest reviews.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value={
                        "count": 12,
                        "next": "http://api.example.com/reviews/latest/?limit=4&offset=4",
                        "previous": None,
                        "results": [
                            {
                                "id": 101,
                                "review_text": "Great lecturer, very clear explanations.",
                                "professor": {
                                    "id": 5,
                                    "first_name": "Alice",
                                    "last_name": "Smith",
                                    "profile_image_url": "/media/professor_profiles/alice.jpg"
                                }
                            },
                            {
                                "id": 100,
                                "review_text": "Challenging exams but fair grading.",
                                "professor": {
                                    "id": 3,
                                    "first_name": "Bob",
                                    "last_name": "Jones",
                                    "profile_image_url": "/media/professor_profiles/bob.png"
                                }
                            },
                            {
                                "id": 99,
                                "review_text": "Very engaging classes!",
                                "professor": {
                                    "id": 8,
                                    "first_name": "Carol",
                                    "last_name": "Davis",
                                    "profile_image_url": None
                                }
                            },
                            {
                                "id": 98,
                                "review_text": "Office hours were extremely helpful.",
                                "professor": {
                                    "id": 7,
                                    "first_name": "Dan",
                                    "last_name": "Wong",
                                    "profile_image_url": "/media/professor_profiles/dan.jpg"
                                }
                            }
                        ]
                    },
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)


professor_reviews_list_schema = extend_schema(
    summary="List Reviews for a Professor",
    description=(
        "Retrieve approved reviews for the specified professor. "
        "Supports filtering by `course_id`, ordering by any of `created_at`, `likes_count`, or `grading`, "
        "and paginated (10 per page)."
    ),
    parameters=[
        OpenApiParameter(
            name="course_id",
            description="Filter reviews to those for the given course ID.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="ordering",
            description=(
                "Comma-separated list of fields to order by. "
                "Prefix with `-` for descending. "
                "Allowed: `created_at`, `likes_count`, `grading`."
            ),
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="page",
            description="Page number (10 reviews per page).",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ReviewRetrieveSerializer(many=True),
            description="A paginated list of reviews for the professor.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value={
                        "count": 25,
                        "next": "http://api.example.com/professors/5/reviews/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": 101,
                                "user": 12,
                                "course": {"id": 7, "name": "Thermodynamics"},
                                "created_at": "2025-05-07T14:30:00Z",
                                "grading": 5,
                                "exam_difficulty": 3,
                                "general_knowledge": 4,
                                "homework_difficulty": 2,
                                "teaching_engagement": 5,
                                "would_take_again": True,
                                "attendance_policy": "mandatory_affects",
                                "received_score": "18.00",
                                "exam_resources": "Textbook + slides",
                                "review_text": "Excellent explanations.",
                                "likes_count": 12,
                                "dislikes_count": 1
                            },
                        ]
                    },
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        404: NOT_FOUND,
        429: TOO_MANY_REQUESTS,
    }
)


my_review_list_schema = extend_schema(
    summary="List Your Reviews for a Professor",
    description="Retrieve the authenticated user's reviews for the specified professor, including pending and approved states.",
    parameters=[
        OpenApiParameter(
            name="pk",
            description="Professor ID whose reviews by the current user are being retrieved.",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=MyReviewRetrieveSerializer(many=True),
            description="A list of reviews by the current user for the professor.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {
                            "id": 42,
                            "user": 7,
                            "course": {"id": 15, "name": "Thermodynamics"},
                            "created_at": "2025-05-07T14:30:00Z",
                            "grading": 5,
                            "exam_difficulty": 3,
                            "general_knowledge": 4,
                            "homework_difficulty": 2,
                            "teaching_engagement": 5,
                            "would_take_again": True,
                            "attendance_policy": "mandatory_affects",
                            "received_score": "18.00",
                            "exam_resources": "Textbook + slides",
                            "review_text": "Excellent explanations.",
                            "likes_count": 12,
                            "dislikes_count": 1,
                            "state": "approved"
                        }
                    ],
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    }
)


review_create_schema = extend_schema(
    summary="Submit a Course Review",
    description=(
        "Allows a verified UI student to submit a review for a specific course. "
        "Each user may submit at most one review per course; duplicates are rejected."
    ),
    request=ReviewCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=ReviewCreateSerializer,
            description="Review submitted successfully; it will be in pending state until approved.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={
                        "user": 12,
                        "course": 5,
                        "state": "pending",
                        "grading": 4,
                        "exam_difficulty": 3,
                        "general_knowledge": 4,
                        "homework_difficulty": 2,
                        "teaching_engagement": 5,
                        "exam_resources": "Textbook & slides",
                        "attendance_policy": "mandatory_affects",
                        "would_take_again": True,
                        "received_score": "18.00",
                        "review_text": "Great explanations and helpful examples!"
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


review_retrieve_schema = extend_schema(
    summary="Retrieve a Specific Review",
    description="Returns detailed information about a specific review by its ID. This endpoint is publicly accessible.",
    responses={
        200: OpenApiResponse(
            response=ReviewRetrieveSerializer,
            description="Detailed review retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Success",
                    value={
                        "id": 42,
                        "user": 8,
                        "course": {
                            "id": 5,
                            "name": "Advanced Algorithms"
                        },
                        "created_at": "2025-05-01T10:30:00Z",
                        "grading": 3,
                        "exam_difficulty": 4,
                        "general_knowledge": 5,
                        "homework_difficulty": 2,
                        "teaching_engagement": 4,
                        "would_take_again": True,
                        "attendance_policy": "mandatory_affects",
                        "received_score": "17.5",
                        "exam_resources": "Past exams and slides",
                        "review_text": "Helpful professor, but the exams were tough.",
                        "likes_count": 12,
                        "dislikes_count": 1
                    },
                    response_only=True
                )
            ],
        ),
        400: BAD_REQUEST,
        401: INVALID_AUTHENTICATION,
        429: TOO_MANY_REQUESTS,
    }
)
