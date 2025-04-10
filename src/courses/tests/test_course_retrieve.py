import pytest
from rest_framework.test import APIClient
from unittest.mock import MagicMock
from django.core.cache import cache


@pytest.fixture
def client():
    client = APIClient()
    client.defaults['HTTP_ACCEPT_LANGUAGE'] = 'en'
    return client


@pytest.fixture
def valid_data():
    return {
        "student_id": "student123",
        "password": "password123"
    }


@pytest.mark.django_db
class TestCoursesRetrieve:

    endpoint = "/course-scheduler/courses/"

    @pytest.mark.django_db
    def test_course_retrieve_validation_error(self, client):
        """
                Test that a course retrieve when raise wrong captcha.
        """
        cache.clear()
        invalid_data = {
            "student_id": "student123",
            "password": "65adsdasd"
        }

        response = client.post(self.endpoint, invalid_data, format='json')
        assert response.status_code == 500 or 400
        assert "detail" in response.data
        assert response.data["detail"] == "internal server error"

    @pytest.mark.django_db
    def test_course_retrieve_wrong_data(self, client, valid_data, mocker):
        """
                Test that a course retrieve with wrong inputs.
        """
        cache.clear()
        mocker.patch('src.crawlers.captcha_solver.captcha_solver.solve', return_value=True)
        mock_crawler = mocker.patch('src.crawlers.crawler.Crawler')
        mock_crawler_instance = mock_crawler.return_value
        mock_crawler_instance.fetch_student_courses.return_value = []
        mock_cleaner = MagicMock()
        mock_cleaner.clean.return_value = None
        mocker.patch('src.utill.cleaners.CrawlerRawDataCleaner', return_value=mock_cleaner)
        mocker.patch('src.courses.services.course_service.bulk_save_courses', return_value=[])
        mocker.patch('src.courses.services.class_session_service.bulk_save_class_sessions')
        mocker.patch('src.courses.services.exam_service.bulk_save_exams')
        response = client.post(self.endpoint, valid_data, format='json')
        assert response.status_code == 500 or 400

