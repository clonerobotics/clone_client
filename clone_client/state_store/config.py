from typing import Optional

from pydantic import BaseSettings, Field

from clone_client.config import ClientConfig, CommunicationService


class StateStoreClientConfig(BaseSettings, ClientConfig):
    """State store client configuration."""

    # pylint: disable=too-few-public-methods

    class Config:
        # pylint: disable=too-few-public-methods, missing-class-docstring
        env_prefix = "STATE_CLIENT_"

    continuous_rpc_timeout = 0.3


class StateStoreConfig(BaseSettings):
    """State store configuration."""

    # pylint: disable=too-few-public-methods

    publisher_web_service: Optional[CommunicationService] = Field(
        CommunicationService(name="golem_state", default_port=4690),
        title="State store publisher Avahi service",
    )


STATE_STORE_CONFIG = StateStoreConfig()
