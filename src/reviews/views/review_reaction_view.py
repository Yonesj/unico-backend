from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from src.utill.permissions import IsUIStudent, IsOwnerOrAdmin
from src.reviews.models import ReviewReaction
from src.reviews.serializers import ReviewReactionCreateSerializer
from src.reviews.serializers.review_reaction_serializer import ReviewReactionRetrieveSerializer, ReviewReactionUpdateSerializer


class MyReviewReactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewReactionRetrieveSerializer

    def get_queryset(self):
        return (
            ReviewReaction.objects
            .select_related('review')
            .filter(user=self.request.user, review__course__professor=self.kwargs['pk'])
        )


class ReviewReactionCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUIStudent]
    serializer_class = ReviewReactionCreateSerializer
    queryset = ReviewReaction.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['review_id'] = self.kwargs['pk']
        return ctx


class ReviewReactionUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    http_method_names = ['patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = ReviewReaction.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ReviewReactionUpdateSerializer
        return ReviewReactionRetrieveSerializer
