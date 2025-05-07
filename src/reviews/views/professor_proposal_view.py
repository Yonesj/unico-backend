from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.utill.permissions import IsUIStudent
from src.reviews.models import ProfessorProposal
from src.reviews.serializers import ProfessorProposalCreateSerializer
from src.reviews.schemas import professor_proposal_create_schema


@professor_proposal_create_schema
class ProfessorProposalCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUIStudent]
    serializer_class = ProfessorProposalCreateSerializer
    queryset = ProfessorProposal.objects.all()
