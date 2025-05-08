from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.reviews.models import ReviewRevision
from src.reviews.serializers import ReviewRevisionCreateSerializer
from src.utill.permissions import IsOwnerOrAdmin
from src.reviews.schemas import review_revision_create_schema


@review_revision_create_schema
class ReviewRevisionCreateView(CreateAPIView):
    queryset = ReviewRevision.objects.all()
    serializer_class = ReviewRevisionCreateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['review_id'] = self.kwargs['pk']
        return ctx
