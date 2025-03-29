from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .deserializers import CourseRawDataDeserializer
from .serializers import GolestanRequestSerializer
from .crawler import Crawler


class CourseRetrieveView(GenericAPIView):
    """
    Get student courses list from Golestan.
    """
    serializer_class = GolestanRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = GolestanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['student_id']
        password = serializer.validated_data['password']
        crawler = Crawler()

        try:
            courses = crawler.fetch_student_courses(username, password)
        except ValueError as e:
            # This catches login failure after max retries (or other value errors)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch-all for any other unexpected errors
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            crawler.close()

        cleaned_courses = []
        errors = []

        for course_data in courses:
            course_serializer = CourseRawDataDeserializer(data=course_data)

            if course_serializer.is_valid():
                course = course_serializer.save()
                cleaned_courses.append(course_serializer.data)
            else:
                errors.append(course_serializer.errors)

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"courses": cleaned_courses}, status=status.HTTP_200_OK)
