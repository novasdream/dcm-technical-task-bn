import os
from tempfile import TemporaryFile
from django.test import TestCase

from api.models import TestRunRequest

from django.core.exceptions import ValidationError

from api.utils import validate_file_name_to_upload

class TestExtendedEnum(TestCase):

    def test_get_as_tuple(self):
        self.assertEqual(
            [
                ('SUCCESS', 'SUCCESS'),
                 ('RUNNING', 'RUNNING'),
                 ('FAILED', 'FAILED'),
                 ('CREATED', 'CREATED'),
                 ('RETRYING', 'RETRYING'),
                 ('FAILED_TO_START', 'FAILED_TO_START')
            ],
            TestRunRequest.StatusChoices.get_as_tuple()
        )

    def test_invalid_file_name(self):
        self.assertRaises(ValidationError, validate_file_name_to_upload, 'teste.txt')

    def test_unsecure_file_name(self):
        self.assertRaises(ValidationError, validate_file_name_to_upload, '__init__.py')
        self.assertRaises(ValidationError, validate_file_name_to_upload, '../teste.txt')
        self.assertRaises(ValidationError, validate_file_name_to_upload, '/teste.py')
        self.assertRaises(ValidationError, validate_file_name_to_upload, '/../../teste.py')
        self.assertRaises(ValidationError, validate_file_name_to_upload, 'teste/../../../teste.py')

        
    def test_valid_file_name(self):
        self.assertEqual(validate_file_name_to_upload('teste.py'), None)
        self.assertEqual(validate_file_name_to_upload('tes.te.py'), None)
        self.assertEqual(validate_file_name_to_upload('tes_)(809203918@#123te.py'), None)