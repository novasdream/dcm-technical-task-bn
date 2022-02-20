from api.utils import handle_uploaded_file
from ionos.settings import BASE_DIR, BASE_DIR_RELATIVE
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
import os
from api.models import TestFilePath, TestRunRequest
from api.serializers import TestRunRequestSerializer, TestRunRequestItemSerializer, UploadNewTestFileSerializer
from api.tasks import execute_test_run_request
from api.usecases import get_assets

class TestRunRequestAPIView(ListCreateAPIView):
    serializer_class = TestRunRequestSerializer
    queryset = TestRunRequest.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        instance = serializer.save()
        execute_test_run_request.delay(instance.id)

class TestFileUploadAPIView(ListCreateAPIView):
    serializer_class = UploadNewTestFileSerializer
                
    def create(self, request):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        newTestFile = request.FILES['file']
        handle_uploaded_file(newTestFile)
        TestFilePath.objects.update_or_create(path=os.path.join(BASE_DIR_RELATIVE, newTestFile.name))

        return Response(status=status.HTTP_201_CREATED)

class TestRunRequestItemAPIView(RetrieveAPIView):
    serializer_class = TestRunRequestItemSerializer
    queryset = TestRunRequest.objects.all()
    lookup_field = 'pk'


class AssetsAPIView(APIView):

    def get(self, request):
        return Response(status=status.HTTP_200_OK, data=get_assets())
