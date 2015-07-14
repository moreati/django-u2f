from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import json

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_otp.models import Device

from u2flib_server import u2f_v2 as u2f

from django_u2f.exceptions import (
    DeviceAlreadyRegistered, DeviceNotRegistered,
    MissingApplicationID, MissingChallenge,
    )
from django_u2f.signals import invalid_counter


def get_available_u2f_methods():
    return [('u2f', _('U2F'))]


class U2FDevice(Device):
    """
    Represents a FIDO Universal 2nd Factor :class:`~django_otp.models.Device`.
    """
    key_handle = models.TextField(
        help_text=_("Opaque reference to the private key, returned by the device during registration."))
    public_key = models.TextField(
        help_text=_("Public key corresponding to the key handle, returned by the device during registration."))
    app_id = models.URLField(
        verbose_name=_("Application ID"),
        help_text=_("Our origin, sent to the device during registration and authentication."))

    counter = models.PositiveIntegerField(
        default=0,
        help_text=_("The non-volatile authentication count last returned by the device."))
    challenge = models.TextField(
        blank=True,
        help_text=_("The last challenge we generated for this device."))

    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Registered"),
        help_text=_("When the device was first registered."))
    last_auth_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Last authenticated"),
        help_text=_("When the device last successfully authenticated."))

    class Meta(Device.Meta):
        verbose_name = _("U2F Device")

    @property
    def registration(self):
        return {
            'publicKey': self.public_key,
            'keyHandle': self.key_handle,
            'appId': self.app_id,
        }

    def is_registered(self):
        return bool(self.key_handle and self.public_key and self.app_id)

    @staticmethod
    def generate_app_id(request):
        if not request.is_secure():
            raise ImproperlyConfigured("U2F requires a secure connection")
        return 'https://{host}'.format(host=request.get_host())

    def generate_register_challenge(self):
        if self.key_handle or self.public_key:
            raise DeviceAlreadyRegistered("This device is already registered")
        if not self.app_id:
            raise MissingApplicationID("An app_id is required to register a U2F device")

        challenge = u2f.start_register(self.app_id)
        self.challenge = json.dumps(challenge)

        # TODO Should we save the instance?
        return _("Activate your U2F device")

    def verify_register_token(self, token):
        if self.key_handle or self.public_key:
            raise DeviceAlreadyRegistered("This device is already registered")
        if not self.challenge:
            raise MissingChallenge("This device has not generated a challenge")

        # TODO Validate and/or save the attestation certificate
        device, attestation_cert = u2f.complete_register(
            self.challenge, token)

        self.key_handle = device['keyHandle']
        self.public_key = device['publicKey']
        self.app_id = device['appId']
        self.challenge = ''
        # TODO Should we save the instance?
        return True

    def generate_challenge(self):
        if not self.is_registered():
            raise DeviceNotRegistered("This device has not been properly registered")

        sign_request = u2f.start_authenticate(self.registration)
        self.challenge = json.dumps(sign_request)
        self.save()

        return _("Activate your U2F device")

    def verify_token(self, token):
        if not (self.key_handle and self.public_key and self.app_id):
            raise DeviceNotRegistered("This device has not been registered")
        if not self.challenge:
            raise MissingChallenge("This device has not generated a challenge")

        try:
            counter, touch_asserted = u2f.verify_authenticate(
                self.registration, self.challenge, token)
        except Exception as e:
            return False

        if counter <= self.counter:
            # Could indicate an attack, e.g. the device has been cloned
            invalid_counter.send(
                sender=self.__class__,
                device=self, challenge=self.challenge, token=token,
                received_counter=counter, last_auth_counter=self.counter,
            )
            return False

        self.counter = counter
        self.last_auth_at = timezone.now()
        self.challenge = ''
        self.save()
        return True
