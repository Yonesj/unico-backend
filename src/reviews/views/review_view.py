from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from src.reviews.models import Review
from src.reviews.serializers import ReviewCreateSerializer, ReviewRetrieveSerializer, ReviewCardSerializer, MyReviewRetrieveSerializer
from src.reviews.paginations import TenPerPagePagination, TopFourItemLimitPagination
from src.utill.permissions import IsUIStudent
from src.reviews.schemas import (
    latest_review_list_schema, professor_reviews_list_schema, my_review_list_schema, review_create_schema, review_retrieve_schema
)


@latest_review_list_schema
class LatestReviewListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ReviewCardSerializer
    pagination_class = TopFourItemLimitPagination

    def get_queryset(self):
        return Review.objects.select_related('course__professor').order_by('-created_at')


@professor_reviews_list_schema
class ProfessorReviewsListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ReviewRetrieveSerializer
    pagination_class = TenPerPagePagination
    # Enable ?course_id=… filter and ?ordering=… sorting
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course_id']
    ordering_fields = ['created_at', 'likes_count', 'grading']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Review.objects
            .with_base_eager_loading()
            .filter(course__professor_id=self.kwargs['pk'])
            .with_stats()
        )


@my_review_list_schema
class MyReviewsByProfessorView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyReviewRetrieveSerializer

    def get_queryset(self):
        return (
            Review.all_objects
            .with_base_eager_loading().with_stats()
            .filter(
                course__professor_id=self.kwargs['pk'],
                user=self.request.user,
            )
        )


class UserReviewListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyReviewRetrieveSerializer

    def get_queryset(self):
        return (
            Review.all_objects
            .with_base_eager_loading().with_stats()
            .filter(user=self.request.user)
        )


@review_create_schema
class ReviewCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUIStudent]
    serializer_class = ReviewCreateSerializer
    queryset = Review.objects.all()


@review_retrieve_schema
class ReviewRetrieveView(RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewRetrieveSerializer
    permission_classes = [AllowAny]
