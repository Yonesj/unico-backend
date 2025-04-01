from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from src.utill.permissions import IsOwnerOrAdmin
from src.courses.models import Plan
from src.courses.serializers import PlanRetrieveSerializer, PlanUpdateSerializer, PlanCreateSerializer, PlanRevokeSerializer
from src.courses.schemas import plan_detail_view_schema, plan_revoke_view_schema, plan_list_create_view_schema, plan_retrieve_shared_view_schema


@plan_list_create_view_schema
class PlanListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PlanCreateSerializer
        return PlanRetrieveSerializer

    def get_queryset(self):
        return Plan.objects.filter(user=self.request.user).prefetch_related('courses')

    def get_serializer_context(self):
        return {'user': self.request.user}


@plan_detail_view_schema
class PlanDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Plan.objects.filter(user=self.request.user).prefetch_related('courses')

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PlanUpdateSerializer
        return PlanRetrieveSerializer


@plan_retrieve_shared_view_schema
class PlanRetrieveView(RetrieveAPIView):
    http_method_names = ['get', 'head', 'option']
    lookup_field = 'share_uuid'
    serializer_class = PlanRetrieveSerializer
    queryset = Plan.objects.all()


@plan_revoke_view_schema
class PlanRevokeAPIView(UpdateAPIView):
    http_method_names = ['put', 'patch']
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = PlanRevokeSerializer
    queryset = Plan.objects.all()
