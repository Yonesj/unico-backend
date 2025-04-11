from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.response import Response

from src.utill.serializers import GolestanRequestSerializer
from src.utill.cleaners import CrawlerRawDataCleaner
from src.courses.serializers import CourseOutputSerializer
from src.crawlers import CourseRetrieveCrawler
from src.courses.services import bulk_save_courses, bulk_save_class_sessions, bulk_save_exams
from src.courses.schemas import course_retrieve_view_schema


@course_retrieve_view_schema
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
        crawler = CourseRetrieveCrawler()

        try:
            courses = crawler.fetch_student_courses(username, password)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": _("internal server error")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            crawler.close()

        cleaner = CrawlerRawDataCleaner()
        cleaned_data_list = [cleaner.clean(course_data) for course_data in courses]
        serialized_courses = CourseOutputSerializer(data=cleaned_data_list, many=True)

        if serialized_courses.is_valid():
            with transaction.atomic():
                saved_courses = bulk_save_courses(cleaned_data_list)
                course_map = {c.id: c for c in saved_courses}
                bulk_save_class_sessions(course_map, cleaned_data_list)
                bulk_save_exams(cleaned_data_list, course_map)

            return Response({"courses": serialized_courses.validated_data}, status=status.HTTP_200_OK)

        return Response({"errors": serialized_courses.errors}, status=status.HTTP_400_BAD_REQUEST)
