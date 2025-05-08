from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from src.utill.permissions import IsUIStudent
from src.reviews.models import ProfessorRevision
from src.reviews.serializers import ProfessorRevisionCreateSerializer
from src.reviews.schemas import professor_revision_create_schema


@professor_revision_create_schema
class ProfessorRevisionCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsUIStudent]
    queryset = ProfessorRevision.objects.all()
    serializer_class = ProfessorRevisionCreateSerializer
