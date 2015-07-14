class DeviceException(Exception):
    pass


class DeviceAlreadyRegistered(DeviceException):
    pass


class DeviceNotRegistered(DeviceException):
    pass


class MissingApplicationID(DeviceException):
    pass


class MissingChallenge(DeviceException):
    pass
