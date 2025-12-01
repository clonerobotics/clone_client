from pydantic_settings import BaseSettings

from clone_client.config import ClientConfig


class StateStoreClientConfig(BaseSettings, ClientConfig):
    """State store client configuration."""

    # pylint: disable=too-few-public-methods

    continuous_rpc_timeout: float = 0.3
