from django.urls import path
from .views import (
    StudentCreateView,
    ProfessorListView,
    ProfessorRetrieveView,
    ProfessorReviewsListView,
    MostPopularProfessorListView,
    MostViewedProfessorListView,
    LatestReviewListView,
    MyReviewReactionListView,
    ReviewReactionCreateView,
    ReviewReportCreateView,
    CourseListCreateView,
    MyReviewsByProfessorView,
    ReviewCreateView,
    ReviewReactionUpdateDestroyView,
    ReviewRetrieveView,
    ReviewRevisionCreateView,
    ProfessorCompareView,
    ProfessorCardRetrieveView,
    FacultyListView,
    ProfessorProposalCreateView,
    ProfessorRevisionCreateView,
    UserReviewListView
)


urlpatterns = [
    path('students/', StudentCreateView.as_view(), name='create-student'),

    path('faculties/', FacultyListView.as_view(), name='list-faculty'),

    path('courses/', CourseListCreateView.as_view(), name='list-create-course'),
    # path('courses/<int:pk>/', TempView.as_view(), name='retrieve-update-course'),
    # path('courses/<int:course_pk>/reviews/', TempView.as_view(), name='list-and-create-review'),

    path('professors/', ProfessorListView.as_view(), name='list-professor'),
    path('professors/proposals/', ProfessorProposalCreateView.as_view(), name='propose-professor'),
    path('professors/most-viewed/', MostViewedProfessorListView.as_view(), name='most-viewed-professors'),
    path('professors/most-popular/', MostPopularProfessorListView.as_view(), name='most-popular-professors'),
    path('professors/compare/', ProfessorCompareView.as_view(), name='compare-professors'),
    path('professors/compare/<int:pk>/', ProfessorCardRetrieveView.as_view(), name='retrieve-professors-comparing'),
    path('professors/<int:pk>/', ProfessorRetrieveView.as_view(), name='retrieve-professor'),
    path('professors/<int:pk>/revisions/', ProfessorRevisionCreateView.as_view(), name='edit-professor'),
    path('professors/<int:pk>/reviews/', ProfessorReviewsListView.as_view(), name='retrieve-professor-reviews'),
    path('professors/<int:pk>/reviews/me/', MyReviewsByProfessorView.as_view(), name='retrieve-user-professor-reviews'),
    path('professors/<int:pk>/reactions/me/', MyReviewReactionListView.as_view(), name='retrieve-my-review-reactions'),

    path('reviews/', ReviewCreateView.as_view(), name='create-review'),
    path('reviews/me/', UserReviewListView.as_view(), name='user-review-list'),
    path('reviews/latest/', LatestReviewListView.as_view(), name='latest-reviews'),
    path('reviews/<int:pk>/', ReviewRetrieveView.as_view(), name='retrieve-review'),
    path('reviews/<int:pk>/reactions/', ReviewReactionCreateView.as_view(), name='create-review-reaction'),
    path('reviews/<int:pk>/reports/', ReviewReportCreateView.as_view(), name='report-review'),
    path('reviews/<int:pk>/revisions/', ReviewRevisionCreateView.as_view(), name='edit-review'),

    path('reactions/<int:pk>/', ReviewReactionUpdateDestroyView.as_view(), name='update-delete-review-reaction'),
]
