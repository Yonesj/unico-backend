from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.utill.permissions import IsUIStudent
from src.reviews.models import ProfessorProposal
from src.reviews.serializers import ProfessorProposalCreateSerializer


class ProfessorProposalCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUIStudent]
    serializer_class = ProfessorProposalCreateSerializer
    queryset = ProfessorProposal.objects.all()
