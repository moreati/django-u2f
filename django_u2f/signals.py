from django.dispatch import Signal


invalid_counter = Signal(
    providing_args=['device', 'challenge', 'token',
                    'recevied_counter', 'last_auth_counter',
                    ])
