from django.urls import path
from .views import CourseRetrieveView


urlpatterns = [
    path('courses/', CourseRetrieveView.as_view(), name='retrieve-courses-from-golestan'),
]
