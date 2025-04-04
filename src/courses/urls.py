from django.urls import path
from .views import CourseRetrieveView, PlanListCreateView, PlanDetailView, PlanRetrieveView, PlanRevokeAPIView


urlpatterns = [
    path('courses/', CourseRetrieveView.as_view(), name='retrieve-courses-from-golestan'),
    path('plans/<int:pk>/revoke/', PlanRevokeAPIView.as_view(), name='plan-link-rovoke'),
    path('plans/<int:pk>/', PlanDetailView.as_view(), name='plan-detail'),
    path('plans/<uuid:share_uuid>/', PlanRetrieveView.as_view(), name='retrieve-shared-plan'),
    path('plans/', PlanListCreateView.as_view(), name='retrieve-create-plans'),
]
