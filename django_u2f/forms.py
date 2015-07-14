from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _

from django_otp.forms import OTPAuthenticationFormMixin

from django_u2f.models import U2FDevice
from django_u2f.validators import (validate_authenticate_response,
                                   validate_register_response,
                                   )


class U2FInput(forms.TextInput):
    class Media:
        js = ('django_u2f/u2f-api.js',)


class U2FHiddenInput(U2FInput):
    input_type = 'hidden'


# TODO These should probably inherit from two_factor.forms.*,
#      but that would create a circular import
class U2FDeviceValidationForm(forms.Form):
    """
    A form that validates the registration response of a new U2F device.
    """
    token = forms.CharField(
        label=_("U2F"),
        validators=[validate_register_response],
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        )
    challenge = forms.CharField(required=False, widget=U2FHiddenInput())
    sign_requests = forms.CharField(required=False, widget=U2FHiddenInput())

    error_messages = {
        'invalid_token': _("The U2F response is not valid."),
        }

    device_class = U2FDevice

    def __init__(self, device, **kwargs):
        super(U2FDeviceValidationForm, self).__init__(**kwargs)
        self.device = device

    def clean_token(self):
        token = self.cleaned_data['token']
        try:
            self.device.verify_register_token(token)
        except Exception as ex:
            raise forms.ValidationError(ex, code='invalid_token')
        return token


class U2FAuthenticationTokenForm(OTPAuthenticationFormMixin, forms.Form):
    otp_token = forms.CharField(
        label=_("U2F"),
        validators=[validate_authenticate_response],
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        )
    challenge = forms.CharField(required=False, widget=U2FHiddenInput())

    def __init__(self, user, initial_device, **kwargs):
        self.user = user
        super(U2FAuthenticationTokenForm, self).__init__(**kwargs)

    def clean(self):
        self.clean_otp(self.user)
        return self.cleaned_data
