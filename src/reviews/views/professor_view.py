from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from src.reviews.models import Professor, ProfessorPageView
from src.reviews.paginations import TopFourItemLimitPagination
from src.reviews.serializers import (
    ProfessorRetrieveSerializer, ProfessorSearchResultSerializer, ProfessorCardSerializer, ProfessorCompareSerializer
)


class ProfessorListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfessorSearchResultSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name', 'courses__name']

    def get_queryset(self):
        return Professor.objects.with_base_eager_loading()


class MostPopularProfessorListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfessorCardSerializer
    pagination_class = TopFourItemLimitPagination

    def get_queryset(self):
        return (
            Professor.objects
            .prefetch_related('courses')
            .with_review_counts()
            .order_by('-overall_rating', '-reviews_count')
        )


class MostViewedProfessorListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfessorCardSerializer
    pagination_class = TopFourItemLimitPagination

    def get_queryset(self):
        return (
            Professor.objects
            .prefetch_related('courses')
            .with_stats()
            .order_by('-views_count', '-reviews_count')
        )


class ProfessorRetrieveView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfessorRetrieveSerializer

    def get_queryset(self):
        return (
            Professor.objects
            .with_base_eager_loading()
            .with_review_counts()
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Overridden to record a search‐log entry whenever an authenticated
        user views a professor.
        """
        instance = self.get_object()

        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')[:256]
        ProfessorPageView.objects.create(professor=instance, ip_address=ip, user_agent=ua)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProfessorCardRetrieveView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfessorCompareSerializer

    def get_queryset(self):
        return (
            Professor.objects
            .with_base_eager_loading()
            .with_review_counts()
        )


class ProfessorCompareView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProfessorCardSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name', 'courses__name']

    def get_queryset(self):
        return Professor.objects.with_base_eager_loading().with_review_counts()
