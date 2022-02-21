import os
from rest_framework import serializers

from api.models import TestRunRequest, TestFilePath, TestEnvironment
from api.utils import validate_file_name_to_upload_input
class UploadNewTestFileSerializer(serializers.Serializer):
    file = serializers.FileField(
        allow_empty_file=False,
        max_length=300,
        validators=[validate_file_name_to_upload_input]
    )


class TestRunRequestSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name'
        )
        read_only_fields = (
            'id',
            'created_at',
            'status',
            'logs',
            'env_name'
        )


class TestRunRequestItemSerializer(serializers.ModelSerializer):
    env_name = serializers.ReadOnlyField(source='env.name')

    class Meta:
        model = TestRunRequest
        fields = (
            'id',
            'requested_by',
            'env',
            'path',
            'status',
            'created_at',
            'env_name',
            'logs'
        )


class TestFilePathSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestFilePath
        fields = ('id', 'path')


class TestEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestEnvironment
        fields = ('id', 'name')
