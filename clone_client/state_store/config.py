from pydantic_settings import BaseSettings

from clone_client.config import ClientConfig


class StateStoreClientConfig(BaseSettings, ClientConfig):
    """State store client configuration."""

    # pylint: disable=too-few-public-methods

    class Config:
        # pylint: disable=too-few-public-methods, missing-class-docstring
        env_prefix = "STATE_CLIENT_"

    continuous_rpc_timeout: float = 0.3
