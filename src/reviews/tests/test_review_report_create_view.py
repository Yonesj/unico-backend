# import pytest
# from django.urls import reverse
# from rest_framework import status
# from src.reviews.models import ReviewReport, ReviewReportChoices, Professor, Course, Review
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model
#
#
# @pytest.fixture
# def api_client():
#     return APIClient()
#
# @pytest.fixture
# def user_factory(db):
#     counter = {'value': 0}
#
#     def create_user(**kwargs):
#         count = counter['value']
#         counter['value'] += 1
#         defaults = {
#             'username': f'user_{kwargs.get("id", count)}',
#             'email': f'user_{kwargs.get("id", count)}@example.com',
#         }
#         defaults.update(kwargs)
#         return get_user_model().objects.create(**defaults)
#
#     return create_user
#
#
# @pytest.fixture
# def professor_factory():
#     def create_professor(**kwargs):
#         defaults = {'first_name': 'Ali', 'last_name': 'Ahmadi'}
#         defaults.update(kwargs)
#         return Professor.objects.create(**defaults)
#
#     return create_professor
#
#
# @pytest.fixture
# def course_factory(professor_factory):
#     def create_course(**kwargs):
#         if 'professor' not in kwargs:
#             kwargs['professor'] = professor_factory()
#         defaults = {'name': 'Test Course'}
#         defaults.update(kwargs)
#         return Course.objects.create(**defaults)
#
#     return create_course
#
#
#
# User = get_user_model()
#
# @pytest.fixture
# def review(user_factory, course_factory):
#     user = user_factory()
#     course = course_factory()
#     return course.reviews.create(
#         user=user,
#         grading=4,
#         exam_difficulty=3,
#         general_knowledge=4,
#         homework_difficulty=2,
#         teaching_engagement=5,
#         attendance_policy='MANDATORY',
#         would_take_again=True,
#         received_score=18.5,
#         review_text="Good course"
#     )
#
# @pytest.fixture
# def review_report_url(review):
#     return reverse("report-review", kwargs={"pk": review.pk})
#
#
# @pytest.mark.django_db
# def test_create_review_report_success(api_client, review, user_factory):
#     user = user_factory()
#     api_client.force_authenticate(user=user)
#
#     url = reverse("report-review", kwargs={"pk": review.pk})
#     print(f"Report URL: {url}")
#     print(f"Review PK: {review.pk}")
#     print(f"Review score: {review.received_score}")
#
#     assert not ReviewReport.objects.filter(reporter=user, review=review).exists()
#
#     data = {
#         "reason": ReviewReportChoices.SPAM,
#     }
#
#     response = api_client.post(url, data=data)
#     print(response.status_code, response.data)
#
#     assert response.status_code == status.HTTP_201_CREATED
#     assert ReviewReport.objects.filter(reporter=user, review=review).exists()
#
# @pytest.mark.django_db
# def test_create_review_report_unauthenticated(api_client, review_report_url):
#     response = api_client.post(review_report_url, data={"reason": ReviewReportChoices.SPAM})
#
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# @pytest.mark.django_db
# def test_create_review_report_nonexistent_review(api_client, user_factory):
#     user = user_factory()
#     api_client.force_authenticate(user=user)
#
#     invalid_url = reverse("report-review", kwargs={"pk": 9999})
#
#     response = api_client.post(invalid_url, data={"reason": ReviewReportChoices.SPAM})
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "Review does not exist" in str(response.data)
#
#
# @pytest.mark.django_db
# def test_create_duplicate_review_report(api_client, review, user_factory):
#     user = user_factory()
#     api_client.force_authenticate(user=user)
#
#     ReviewReport.objects.create(reporter=user, review=review, reason=ReviewReportChoices.SPAM)
#
#     url = reverse("report-review", kwargs={"pk": review.pk})
#     response = api_client.post(url, data={"reason": ReviewReportChoices.SPAM})
#
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert "already reported" in str(response.data["non_field_errors"])
