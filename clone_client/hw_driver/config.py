from pydantic_settings import BaseSettings

from clone_client.config import ClientConfig


class HWDriverClientConfig(BaseSettings, ClientConfig):
    """Hardware Driver client configuration."""

    # pylint: disable=too-few-public-methods

    continuous_rpc_timeout: float = 0.3
