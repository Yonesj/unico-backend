from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.reviews.models import ReviewReport
from src.reviews.serializers import ReviewReportCreateSerializer


class ReviewReportCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewReportCreateSerializer
    queryset = ReviewReport.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['review_id'] = self.kwargs['pk']
        return ctx
