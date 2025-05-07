from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.reviews.models.professor_revision import ProfessorRevision
from src.reviews.serializers.professor_revision_serializer import ProfessorRevisionCreateSerializer


class ProfessorRevisionCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ProfessorRevision.objects.all()
    serializer_class = ProfessorRevisionCreateSerializer
