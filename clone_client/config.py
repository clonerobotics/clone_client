from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


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
    default_unix_sock_name: str = ""


class CommunicationConfig(BaseModel):
    """Communication configuration."""

    # pylint: disable=too-few-public-methods

    controller_service: CommunicationService = CommunicationService(
        name="golem_controller", default_port=4689, default_unix_sock_name="controller.socket"
    )
    state_store_service: CommunicationService = Field(
        CommunicationService(
            name="golem_state", default_port=4690, default_unix_sock_name="state_store_rcv.socket"
        ),
        title="State store publisher Avahi service",
    )
    hw_driver_service: CommunicationService = CommunicationService(
        name="golem_hardware_driver", default_port=4692, default_unix_sock_name="hardware_driver.socket"
    )


class Config(BaseSettings):
    """Application configuration."""

    # pylint: disable=too-few-public-methods

    communication: CommunicationConfig = Field(CommunicationConfig(), title="Communication configuration")


CONFIG: Config = Config()
