from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.utill.serializers import GolestanRequestSerializer
from src.crawlers import StudentValidatorCrawler
from src.reviews.models import Student
from src.reviews.schemas import student_create_view_schema


@student_create_view_schema
class StudentCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GolestanRequestSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_ui_student:
            return Response({"detail": _("you already have a profile")}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        golestan_username = serializer.validated_data['student_id']
        golestan_password = serializer.validated_data['password']
        crawler = StudentValidatorCrawler()

        try:
            student_info = crawler.fetch_student_info(golestan_username, golestan_password)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": _("internal server error")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            crawler.close()

        with transaction.atomic():
            user = request.user
            user.full_name = student_info['full_name']
            user.is_ui_student = True
            user.save()

            Student.objects.create(
                student_id=student_info['student_id'],
                user=user,
                faculty=student_info['faculty'],
                major=student_info['major']
            )

        return Response({"detail": _("your profile were created successfully")}, status=status.HTTP_201_CREATED)
