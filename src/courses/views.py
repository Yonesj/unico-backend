import base64

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import GolestanRequestSerializer
from .crawler import Crawler

class CourseRetrieveView(GenericAPIView):
    """
    Get student courses list from Golestan.
    """
    serializer_class = GolestanRequestSerializer

    def post(self, request):
        serializer = GolestanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['student_id']
        password = serializer.validated_data['password']
        crawler = Crawler()
        return Response({'image': crawler.fetch_student_courses(str(username), password)}, status=status.HTTP_200_OK)

        # try:
        #     activation_obj = ActivationCode.objects.get(code=code)
        # except ActivationCode.DoesNotExist:
        #     return Response({'detail': 'Invalid activation code.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # user = activation_obj.user
        #
        # if user.is_active:
        #     return Response({'detail': 'User is already activated.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # now = timezone.now()
        # if not activation_obj.created_at or now > activation_obj.created_at + timedelta(minutes=10):
        #     return Response({'detail': 'Activation code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # user.is_active = True
        # user.save(update_fields=['is_active'])
        # activation_obj.delete()
        #
        # return Response({'detail': 'User activated successfully.'}, status=status.HTTP_200_OK)
