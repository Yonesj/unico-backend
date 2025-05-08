from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from src.utill.permissions import IsUIStudent, IsOwnerOrAdmin
from src.reviews.models import ReviewReaction
from src.reviews.serializers import ReviewReactionCreateSerializer
from src.reviews.serializers import ReviewReactionRetrieveSerializer, ReviewReactionUpdateSerializer
from src.reviews.schemas import (
    review_reaction_create_schema, review_reaction_update_destroy_schema, my_review_reaction_list_schema
)


@my_review_reaction_list_schema
class MyReviewReactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewReactionRetrieveSerializer

    def get_queryset(self):
        return (
            ReviewReaction.objects
            .select_related('review')
            .filter(user=self.request.user, review__course__professor=self.kwargs['pk'])
        )


@review_reaction_create_schema
class ReviewReactionCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUIStudent]
    serializer_class = ReviewReactionCreateSerializer
    queryset = ReviewReaction.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['review_id'] = self.kwargs['pk']
        return ctx


@review_reaction_update_destroy_schema
class ReviewReactionUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    http_method_names = ['patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = ReviewReaction.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ReviewReactionUpdateSerializer
        return ReviewReactionRetrieveSerializer
