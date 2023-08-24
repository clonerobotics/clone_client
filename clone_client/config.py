from typing import Optional

from pydantic import BaseModel, BaseSettings, Field


class ClientConfig(BaseModel):
    """Client configuration."""

    # pylint: disable=too-few-public-methods

    continuous_rpc_timeout: Optional[float] = Field(
        None, description="Timeout in seconds for RPCs that happen continuously, like e.g. valve control"
    )
    critical_rpc_timeout: Optional[float] = Field(
        None,
        description="Timeout in seconds for RPCs that require one critical response, like e.g. starting pump",
    )
    info_gathering_rpc_timeout: float = Field(
        6.0,
        description="Timeout in seconds for RPCs that require to gather information, like e.g. getting nodes",
    )


class CommunicationService(BaseModel):
    """Communication service configuration."""

    # pylint: disable=too-few-public-methods

    name: str
    default_port: int = 1234


class CommunicationConfig(BaseModel):
    """Communication configuration."""

    # pylint: disable=too-few-public-methods

    controller_service: CommunicationService = CommunicationService(
        name="golem_controller", default_port=4689
    )


class Config(BaseSettings):
    """Application configuration."""

    # pylint: disable=too-few-public-methods

    class Config:
        # pylint: disable=too-few-public-methods, missing-class-docstring
        env_prefix = "CONFIG_"
        env_nested_delimiter = "__"

    communication: CommunicationConfig = Field(CommunicationConfig(), title="Communication configuration")
    max_retries: int = Field(3, title="Maximum number of retries before failing.")
    delay: int = Field(1, title="Delay between retries in seconds.")


CONFIG: Config = Config()
