from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from src.courses.serializers import CourseOutputSerializer
from src.utill.general_schemas import BAD_REQUEST, TOO_MANY_REQUESTS
from src.utill.serializers import GolestanRequestSerializer


course_retrieve_view_description = """
This endpoint retrieves a list of courses from Golestan using the provided student credentials.

### 🔑 Expected Flow:
1. **POST Request**: The client sends a payload with:
   - `student_id`: The student's ID.
   - `password`: The student's password.
2. The backend uses a crawler to log in to Golestan and fetch raw course data.
3. Raw data is cleaned using a dedicated cleaner (e.g., `CrawlerRawDataCleaner`).
4. Cleaned data is bulk saved/updated in the database.
5. The endpoint returns a JSON object with a `courses` key. If no courses are found, an empty list is returned.

### ⚙️ Security and Error Considerations:
- Invalid credentials or other validation issues yield a **400 Bad Request**.
- Any unexpected error from the crawler is mapped to a **500 Internal Server Error**.
- The endpoint may be rate-limited, returning **429 Too Many Requests** if exceeded.
"""

course_retrieve_view_schema = extend_schema(
    summary="Retrieve Courses from Golestan",
    description=course_retrieve_view_description,
    request=GolestanRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=CourseOutputSerializer,
            description=(
                "Courses retrieved successfully. "
                "If no courses are found, the response will be `{'courses': []}`."
            ),
            examples=[
                OpenApiExample(
                    name="Successful Response",
                    value={
                        "courses": [
                            {
                                "id": 121231701,
                                "course_code": "1212317_01",
                                "course_name": "فارسي عمومي",
                                "theory": "3",
                                "practical": "0",
                                "capacity": 50,
                                "gender": "B",
                                "professor_name": "حسين پورجيرهنده مرجان",
                                "class_location": "ادبيات و علوم انساني _ 15 - طبقه اول - ادبيات",
                                "prerequisites": "1212318 زبان فارسي معادل: 1612211 فارسي عمومي معادل: 1616059 فارسي عمومي",
                                "notes": "",
                                "classes": [
                                    {"day": "sun", "start": 10, "end": 12},
                                    {"day": "tue", "start": 14, "end": 15}
                                ],
                                "exam": {
                                    "date": "1404.03.26",
                                    "start": 10,
                                    "end": 12
                                }
                            }
                        ]
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    name="Empty Response",
                    value={"courses": []},
                    response_only=True,
                )
            ],
        ),
        400: BAD_REQUEST,
        429: TOO_MANY_REQUESTS,
        500: OpenApiResponse(
            description="Internal server error.",
            examples=[
                OpenApiExample(
                    name="Internal Server Error",
                    value={"detail": "internal server error"},
                    response_only=True,
                )
            ],
        ),
    },
)
