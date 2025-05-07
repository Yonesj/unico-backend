from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from src.reviews.models import Course
from src.reviews.serializers import CourseSummarySerializer
from src.reviews.schemas import course_list_view_schema


@course_list_view_schema
class CourseListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Course.objects.all()
    serializer_class = CourseSummarySerializer

    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['faculty_id']
    search_fields = ['name']
