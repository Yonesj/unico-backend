from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from src.reviews.serializers import (
    ProfessorSearchResultSerializer, ProfessorCardSerializer, ProfessorRetrieveSerializer,
    ProfessorCompareSerializer
)
from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS, NOT_FOUND


professor_list_view_schema = extend_schema(
    summary="Search Professors",
    description="Return a list of professors matching the optional `search` query on first name, last name, or course name.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Case-insensitive partial match against professor first name, last name, or course name."
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProfessorSearchResultSerializer(many=True),
            description="A list of matching professors.",
            examples=[
                OpenApiExample(
                    name="Search Response",
                    value=[
                        {
                            "id": 5,
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "profile_image": "/media/professor_profiles/alice.jpg",
                            "courses": [
                                {"id": 12, "name": "Intro to Biology"},
                                {"id": 24, "name": "Genetics"}
                            ]
                        },
                        {
                            "id": 8,
                            "first_name": "Albert",
                            "last_name": "Jones",
                            "profile_image": "/media/professor_profiles/albert.png",
                            "courses": [
                                {"id": 33, "name": "Advanced Genetics"}
                            ]
                        }
                    ],
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)


most_viewed_professors_schema = extend_schema(
    summary="List Most Viewed Professors",
    description="Returns professors ordered by view count (then review count), with limit/offset pagination.",
    parameters=[
        OpenApiParameter(
            name="limit",
            description="Maximum number of items to return (default 4, max 10).",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="offset",
            description="Offset into the result set.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProfessorCardSerializer(many=True),
            description="A paginated list of the most viewed professors.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {
                            "id": 3,
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "profile_image": "/media/professor_profiles/alice.jpg",
                            "overall_rating": "4.75",
                            "reviews_count": 120,
                            "courses": [
                                {"id": 10, "name": "Calculus I"},
                                {"id": 11, "name": "Linear Algebra"}
                            ]
                        },
                        {
                            "id": 7,
                            "first_name": "Bob",
                            "last_name": "Jones",
                            "profile_image": "/media/professor_profiles/bob.png",
                            "overall_rating": "4.60",
                            "reviews_count": 98,
                            "courses": [
                                {"id": 22, "name": "Physics I"}
                            ]
                        }
                    ],
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)


most_popular_professors_schema = extend_schema(
    summary="List Most Popular Professors",
    description="Returns professors ordered by overall rating and review count, with limit/offset pagination.",
    parameters=[
        OpenApiParameter(
            name="limit",
            description="Maximum number of items to return (default 4, max 10).",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="offset",
            description="Offset into the result set.",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProfessorCardSerializer(many=True),
            description="A paginated list of the most popular professors.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {
                            "id": 5,
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "profile_image": "/media/professor_profiles/alice.jpg",
                            "overall_rating": "4.85",
                            "reviews_count": 150,
                            "courses": [
                                {"id": 12, "name": "Calculus I"},
                                {"id": 18, "name": "Linear Algebra"}
                            ]
                        },
                        {
                            "id": 8,
                            "first_name": "Bob",
                            "last_name": "Jones",
                            "profile_image": "/media/professor_profiles/bob.png",
                            "overall_rating": "4.78",
                            "reviews_count": 120,
                            "courses": [
                                {"id": 22, "name": "Physics I"}
                            ]
                        }
                    ],
                    response_only=True
                )
            ]
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)


professor_retrieve_view_schema = extend_schema(
    summary="Retrieve Professor Details",
    description="Get full details for a single professor, including courses, ratings, and related professors. "
                "Also logs the page view for authenticated users.",
    responses={
        200: OpenApiResponse(
            response=ProfessorRetrieveSerializer,
            description="Professor retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value={
                        "id": 42,
                        "overall_rating": "4.75",
                        "reviews_count": 128,
                        "profile_image": "/media/professor_profiles/jdoe.jpg",
                        "first_name": "John",
                        "last_name": "Doe",
                        "faculty": "Engineering",
                        "courses": [
                            {"id": 7, "name": "Thermodynamics"},
                            {"id": 8, "name": "Fluid Mechanics"}
                        ],
                        "office_number": "B12",
                        "telegram_account": "@johndoe",
                        "email": "j.doe@university.edu",
                        "website_url": "https://johndoe.example.com",
                        "office_location": "Building A, Room 101",
                        "schedule_image": "/media/professor_schedules/jdoe_schedule.png",
                        "student_scores_avg": "17.50",
                        "average_would_take_again": "4.90",
                        "related_professors": [
                            {"id": 43, "first_name": "Jane", "last_name": "Smith", "profile_image": "/media/..."},
                            {"id": 44, "first_name": "Alan", "last_name": "Brown", "profile_image": None}
                        ],
                        "grading_avg": "4.80",
                        "general_knowledge_avg": "4.70",
                        "teaching_engagement_avg": "4.90",
                        "exam_difficulty_avg": "3.20",
                        "homework_difficulty_avg": "2.80"
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


professor_card_retrieve_schema = extend_schema(
    summary="Retrieve Professor Card Details",
    description="Fetch a compact set of professor information for comparison purposes, including ratings, course list, and faculty.",
    responses={
        200: OpenApiResponse(
            response=ProfessorCompareSerializer,
            description="Professor details for comparison retrieved successfully.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value={
                        "id": 42,
                        "overall_rating": "4.75",
                        "reviews_count": 128,
                        "first_name": "John",
                        "last_name": "Doe",
                        "faculty": "Engineering",
                        "courses": [
                            {"id": 7, "name": "Thermodynamics"},
                            {"id": 8, "name": "Fluid Mechanics"}
                        ],
                        "grading_avg": "4.80",
                        "general_knowledge_avg": "4.70",
                        "teaching_engagement_avg": "4.90",
                        "exam_difficulty_avg": "3.20",
                        "homework_difficulty_avg": "2.80",
                        "student_scores_avg": "17.50",
                        "average_would_take_again": "4.90"
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


professor_compare_view_schema = extend_schema(
    summary="Search and Compare Professors",
    description="Return a list of professors (for comparison) filtered by optional `search` term on first name, last name, or course name.",
    parameters=[
        OpenApiParameter(
            name="search",
            description="Case-insensitive partial match against professor first name, last name, or course name.",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProfessorCardSerializer(many=True),
            description="A list of professors matching the search criteria.",
            examples=[
                OpenApiExample(
                    name="Example Response",
                    value=[
                        {
                            "id": 5,
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "profile_image": "/media/professor_profiles/alice.jpg",
                            "overall_rating": "4.85",
                            "reviews_count": 150,
                            "courses": [
                                {"id": 12, "name": "Calculus I"},
                                {"id": 18, "name": "Linear Algebra"}
                            ]
                        },
                        {
                            "id": 8,
                            "first_name": "Bob",
                            "last_name": "Jones",
                            "profile_image": "/media/professor_profiles/bob.png",
                            "overall_rating": "4.78",
                            "reviews_count": 120,
                            "courses": [
                                {"id": 22, "name": "Physics I"}
                            ]
                        }
                    ],
                    response_only=True,
                )
            ]
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
    }
)
