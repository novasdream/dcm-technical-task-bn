import logging
from enum import Enum
import os
from typing import List, Tuple

from django.core.exceptions import ValidationError

from ionos.settings import BASE_DIR, BASE_DIR_RELATIVE, BASE_DIR_UPLOADS
logger = logging.getLogger(__name__)

class ExtendedEnum(Enum):
    @classmethod
    def get_as_tuple(cls) -> List[Tuple]:
        #  return str representation of value to allow for objects as values
        return [(item.name, str(item.value)) for item in cls]

def validate_file_name_to_upload_input(file):
    validate_file_name_to_upload(file.name)

def validate_file_name_to_upload(file_name):
    # resolves symbolic links
    if not file_name.endswith('.py'):
        raise ValidationError('Filename is not a python file.')
    if file_name == '__init__.py':
        raise ValidationError('Filename is invalid.')
    
    file_destination = os.path.join(BASE_DIR_UPLOADS, file_name)

    matchpath = os.path.realpath(file_destination)

    if not (BASE_DIR_UPLOADS == os.path.commonpath((BASE_DIR_UPLOADS, matchpath))):
        logging.error('[UnsecureFileName] This filename [' + file_name + '] possible is trying to access to a file outside of project.')
        raise ValidationError('Filename is invalid.')

def handle_uploaded_file(f):
    file_destination = os.path.join(BASE_DIR_UPLOADS, f.name)
    with open(os.path.join(file_destination), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)