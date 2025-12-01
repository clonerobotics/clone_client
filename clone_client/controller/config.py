from pydantic_settings import BaseSettings

from clone_client.config import ClientConfig


class ControllerClientConfig(BaseSettings, ClientConfig):
    """Controller client configuration."""

    # pylint: disable=too-few-public-methods

    critical_rpc_timeout: float = 0.5
    continuous_rpc_timeout: float = 0.1
