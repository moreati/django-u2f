from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import json

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _, ungettext


REQUIRED_AUTHENTICATE_KEYS = (
    'clientData',
    'keyHandle',
    'signatureData',
    )

REQUIRED_REGISTER_KEYS = (
    'appId',
    'challenge',
    'clientData',
    'registrationData',
    )

def validate_response(value, required_keys):
    try:
        value = json.loads(value)
    except ValueError:
        raise ValidationError(_('Enter a JSON object.'),
                              code='invalid')

    if not isinstance(value, dict):
        raise ValidationError(_('Enter a JSON object.'),
                              code='invalid')

    if 'errorCode' in value:
        raise ValidationError(_('Contains an errorCode: %(errorCode)s.'),
                              params={'errorCode': value['errorCode']},
                              code='errorCode')

    missing_keys = [key for key in required_keys if key not in value]
    if missing_keys:
        raise ValidationError(ungettext('Missing key: %(keys)s.',
                                        'Missing keys: %(keys)s.',
                                        len(missing_keys)),
                              params={'keys': ', '.join(missing_keys)},
                              code='missing_keys')


def validate_authenticate_response(value):
    return validate_response(value, REQUIRED_AUTHENTICATE_KEYS)


def validate_register_response(value):
    return validate_response(value, REQUIRED_REGISTER_KEYS)
