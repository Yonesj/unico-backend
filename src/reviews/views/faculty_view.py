from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from src.reviews.models import Faculty
from src.reviews.serializers import FacultyRetrieveSerializer


class FacultyListView(ListAPIView):
    queryset = Faculty.objects.all()
    permission_classes = [AllowAny]
    serializer_class = FacultyRetrieveSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
