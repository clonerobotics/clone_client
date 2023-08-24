class ClientError(Exception):
    """Basic, application specific error which indicates bad software usage."""


class DesiredPressureNotAchievedError(ClientError):
    """Indicates that the desired pressure was not achieved in the given time."""

    def __init__(self, timeout_ms: int) -> None:
        message = f"Couldn't achieve desired pressure after {timeout_ms} milliseconds"
        super().__init__(message)


class MissingConfigurationError(ClientError):
    """Indicates that the configuration for a given element is missing."""

    def __init__(self, element: str) -> None:
        message = f"Missing configuration for {element}"
        super().__init__(message)
