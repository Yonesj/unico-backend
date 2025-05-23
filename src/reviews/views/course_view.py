from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from src.reviews.models import Course, State
from src.reviews.serializers import CourseSummarySerializer, CourseCreateSerializer
from src.reviews.schemas import course_list_view_schema


@course_list_view_schema
class CourseListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Course.objects.filter(state=State.APPROVED)

    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['faculty_id']
    search_fields = ['name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseSummarySerializer
