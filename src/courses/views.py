from django.db import transaction
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from src.utill.cleaners import CrawlerRawDataCleaner
from .serializers import GolestanRequestSerializer, CourseOutputSerializer
from .crawler import Crawler
from .services import bulk_save_courses, bulk_update_class_sessions


class CourseRetrieveView(GenericAPIView):
    """
    Get student courses list from Golestan.
    """
    serializer_class = GolestanRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
            return Response({"detail": "internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            crawler.close()

        cleaner = CrawlerRawDataCleaner()
        cleaned_data_list = [cleaner.clean(course_data) for course_data in courses]
        serialized_courses = CourseOutputSerializer(data=cleaned_data_list, many=True)

        if serialized_courses.is_valid():
            with transaction.atomic():
                saved_courses = bulk_save_courses(cleaned_data_list)
                course_map = {c.id: c for c in saved_courses}
                bulk_update_class_sessions(course_map, cleaned_data_list)

            return Response({"courses": serialized_courses.validated_data}, status=status.HTTP_200_OK)

        return Response({"errors": serialized_courses.errors}, status=status.HTTP_400_BAD_REQUEST)
