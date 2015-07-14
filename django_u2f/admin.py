from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from django_u2f.models import U2FDevice


class U2FDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~django_u2f.models.U2FDevice`.
    """
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
            }),
        ('Configuration', {
            'fields': ['key_handle', 'public_key', 'app_id'],
            }),
        ('State', {
            'fields': ['counter', 'challenge', 'last_auth_at'],
            }),
        ]


try:
    admin.site.register(U2FDevice, U2FDeviceAdmin)
except AlreadyRegistered:
    # A useless exception from a double import
    pass
