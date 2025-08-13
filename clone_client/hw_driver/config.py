from pydantic_settings import BaseSettings

from clone_client.config import ClientConfig


class HWDriverClientConfig(BaseSettings, ClientConfig):
    """Hardware Driver client configuration."""

    # pylint: disable=too-few-public-methods

    class Config:
        # pylint: disable=too-few-public-methods, missing-class-docstring
        env_prefix = "HW_CLIENT_"

    continuous_rpc_timeout: float = 0.3
